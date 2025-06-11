import joblib
import json
import os
import numpy as np
import pandas as pd
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .forms import MentalHealthForm, UserRegistrationForm
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm
from .forms import ProfileForm, UserUpdateForm,ContactForm
from .models import UserResponse, Prediction
from django.core.mail import send_mail
from django.views import View

# Initialize logger
logger = logging.getLogger(__name__)

# Define the expected features in the exact order your model expects them
expected_features = [
    'Age', 'Course', 'Gender', 'CGPA', 'Sleep_Quality', 'Social_Support',
    'Relationship_Status', 'Substance_Use', 'Counseling_Service_Use',
    'Semester_Credit_Load', 'Family_History', 'Chronic_Illness',
    'Extracurricular_Involvement', 'Residence_Type', 'Physical_Activity',
    'Diet_Quality', 'Financial_Stress'
]

# Load all required models and preprocessing objects
model_dir = os.path.join(settings.BASE_DIR, 'userApp', 'Ml_models')

try:
    ada_model = joblib.load(os.path.join(model_dir, 'multioutput_adaboost_model.joblib'))
    feature_selector = joblib.load(os.path.join(model_dir, 'feature_selector_Ada.joblib'))
    scaler = joblib.load(os.path.join(model_dir, 'scaler_Ada.joblib'))
except Exception as e:
    logger.error(f"Failed to load ML models: {str(e)}")
    raise ImportError(f"Failed to load ML models: {str(e)}")

def clean_numeric_input(value):
    """Clean and convert numeric input to float"""
    if value is None:
        return 0.0
    if isinstance(value, str):
        # Remove any non-numeric characters except decimal point and minus
        value = ''.join(c for c in value if c.isdigit() or c in {'.', '-'})
        if not value:  # Handle empty string after cleaning
            return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0  # Default value if conversion fails

def manual_encode(df):
    gender_map = {'Male': 0, 'Female': 1, 'Others': 2}
    sleep_quality_map = {'Good': 0, 'Average': 1, 'Poor': 2}
    social_support_map = {'Low': 0, 'Moderate': 1, 'High': 2}
    relationship_map = {'Single': 0, 'In a relationship': 1, 'Married': 2}
    substance_use_map = {'Never': 0, 'Occasionally': 1, 'Frequently': 2}
    counseling_map = {'Never': 0, 'Occasionally': 1, 'Frequently': 2}
    course_map = {
        'Engineering': 0, 'Business': 1, 'Computer': 2,
        'Law': 3, 'Medical': 4, 'Other': 5
    }
    activity_map = {'Low': 0, 'Moderate': 1, 'High': 2}
    diet_map = {'Good': 0, 'Average': 1, 'Poor': 2}
    residence_map = {'On-Campus': 0, 'Off-Campus': 1, 'With Family': 2}
    binary_map = {'Yes': 1, 'No': 0}

    df['Gender'] = df['Gender'].map(gender_map)
    df['Sleep_Quality'] = df['Sleep_Quality'].map(sleep_quality_map)
    df['Social_Support'] = df['Social_Support'].map(social_support_map)
    df['Relationship_Status'] = df['Relationship_Status'].map(relationship_map)
    df['Substance_Use'] = df['Substance_Use'].map(substance_use_map)
    df['Counseling_Service_Use'] = df['Counseling_Service_Use'].map(counseling_map)
    df['Course'] = df['Course'].map(course_map)
    df['Extracurricular_Involvement'] = df['Extracurricular_Involvement'].map(activity_map)
    df['Residence_Type'] = df['Residence_Type'].map(residence_map)
    df['Physical_Activity'] = df['Physical_Activity'].map(activity_map)
    df['Diet_Quality'] = df['Diet_Quality'].map(diet_map)
    df['Family_History'] = df['Family_History'].map(binary_map)
    df['Chronic_Illness'] = df['Chronic_Illness'].map(binary_map)
    df['Financial_Stress'] = df['Financial_Stress'].apply(clean_numeric_input)

    return df

def preprocess_user_data(user_data):
    # Clean all numeric inputs first
    numeric_fields = ['age', 'cgpa', 'semester_credit_load', 'financial_stress']
    for field in numeric_fields:
        user_data[field] = clean_numeric_input(user_data.get(field, 0))

    processed_data = {
        'Age': user_data['age'],
        'Course': user_data['course'],
        'Gender': user_data['gender'],
        'CGPA': user_data['cgpa'],
        'Sleep_Quality': user_data['sleep_quality'],
        'Social_Support': user_data['social_support'],
        'Relationship_Status': user_data['relationship_status'],
        'Substance_Use': user_data['substance_use'],
        'Counseling_Service_Use': user_data['counseling_service_use'],
        'Semester_Credit_Load': user_data['semester_credit_load'],
        'Family_History': user_data['family_history'],
        'Chronic_Illness': user_data['chronic_illness'],
        'Extracurricular_Involvement': user_data['extracurricular_involvement'],
        'Residence_Type': user_data['residence_type'],
        'Physical_Activity': user_data['physical_activity'],
        'Diet_Quality': user_data['diet_quality'],
        'Financial_Stress': user_data['financial_stress'],
    }
    
    # Create DataFrame with exactly the expected features in the right order
    df = pd.DataFrame([processed_data], columns=expected_features)
    df = manual_encode(df)
    
    numpy_data = df.values.astype(float)
    scaled_data = scaler.transform(numpy_data)
    selected_features = feature_selector.transform(scaled_data)
    
    logger.debug(f"Processed data shape: {selected_features.shape}")
    return selected_features

def generate_user_insights(user_data, model):
    predictions = model.predict(user_data)

    stress_thresholds = [2, 3.5]
    depression_thresholds = [2, 3.5]
    anxiety_thresholds = [2, 3.5]

    stress_level = "Low" if predictions[0][0] < stress_thresholds[0] else \
                  "Moderate" if predictions[0][0] < stress_thresholds[1] else "High"

    depression_level = "Low" if predictions[0][1] < depression_thresholds[0] else \
                      "Moderate" if predictions[0][1] < depression_thresholds[1] else "High"

    anxiety_level = "Low" if predictions[0][2] < anxiety_thresholds[0] else \
                   "Moderate" if predictions[0][2] < anxiety_thresholds[1] else "High"

    def get_stress_recommendations(stress_level, user_data):
        if stress_level == "High":
            return [
                "Practice mindfulness and relaxation techniques",
                "Consider seeking professional help",
                "Prioritize sleep and healthy eating",
                "Take regular breaks during work/study (5 min every hour)"
            ]
        elif stress_level == "Moderate":
            return [
                "Maintain a healthy lifestyle with balanced diet and regular exercise",
                "Practice daily mindfulness or meditation (10-15 minutes)",
                "Establish a consistent sleep schedule (7-9 hours)",
                "Connect with friends and family"
            ]
        else:
            return [
                "Continue with stress-reducing activities",
                "Practice gratitude journaling (3 things daily)",
                "Engage in regular physical activity",
                "Maintain work-life balance"
            ]

    def get_depression_recommendations(depression_level, user_data):
        if depression_level == "High":
            return [
                "Seek professional help immediately",
                "Prioritize sleep and healthy eating",
                "Engage in activities you enjoy",
                "Connect with support groups or trusted friends"
            ]
        elif depression_level == "Moderate":
            return [
                "Consider talking to a therapist or counselor",
                "Establish a daily routine with achievable goals",
                "Practice self-care activities",
                "Try progressive muscle relaxation techniques"
            ]
        else:
            return [
                "Maintain a positive outlook",
                "Continue with activities that promote mental well-being",
                "Practice gratitude journaling (3 things daily)",
                "Engage in social activities"
            ]

    def get_anxiety_recommendations(anxiety_level, user_data):
        if anxiety_level == "High":
            return [
                "Consult with a mental health professional",
                "Practice deep breathing exercises (4-7-8 technique)",
                "Limit caffeine and alcohol intake",
                "Establish a worry time (15-20 minutes scheduled)"
            ]
        elif anxiety_level == "Moderate":
            return [
                "Engage in relaxation techniques",
                "Challenge negative thoughts",
                "Consider joining a support group",
                "Try progressive muscle relaxation techniques"
            ]
        else:
            return [
                "Maintain a healthy lifestyle",
                "Continue with anxiety-reducing practices",
                "Practice mindfulness exercises",
                "Establish a consistent daily routine"
            ]

    insights = {
        'stress': {
            'score': float(predictions[0][0]),
            'level': stress_level,
            'recommendations': get_stress_recommendations(stress_level, user_data)
        },
        'depression': {
            'score': float(predictions[0][1]),
            'level': depression_level,
            'recommendations': get_depression_recommendations(depression_level, user_data)
        },
        'anxiety': {
            'score': float(predictions[0][2]),
            'level': anxiety_level,
            'recommendations': get_anxiety_recommendations(anxiety_level, user_data)
        }
    }

    return insights


def generate_explanation(prediction):
    try:
        stress, depression, anxiety = prediction[0]
        explanations = []

        if stress >= 4:
            explanations.append("High stress level detected - consider stress management techniques such as mindfulness, exercise, or counseling.")
            explanations.append("Chronic high stress can impact physical health - monitor blood pressure and sleep patterns regularly.")
            explanations.append("Consider identifying specific stress triggers through journaling to better manage them.")
        elif stress >= 2:
            explanations.append("Moderate stress level - monitor your stress regularly and try healthy coping mechanisms.")
            explanations.append("Even moderate stress can accumulate - schedule regular relaxation breaks throughout your day.")
            explanations.append("Physical activity like walking or yoga can help moderate stress levels effectively.")
        else:
            explanations.append("Your stress level appears within the normal range.")
            explanations.append("Maintaining healthy habits will help keep your stress levels in check.")
            explanations.append("Regular self-check-ins can help detect early signs of increasing stress.")

        if depression >= 4:
            explanations.append("High depression score - seeking support from a mental health professional is recommended.")
            explanations.append("Persistent depression may affect daily functioning - consider reaching out to support networks.")
            explanations.append("Small, manageable goals can help create positive momentum when dealing with depression.")
        elif depression >= 2:
            explanations.append("Moderate depression score - be aware of changes in mood and talk to someone you trust.")
            explanations.append("Maintaining social connections can help prevent moderate depression from worsening.")
            explanations.append("Morning sunlight exposure and regular sleep patterns may help improve mood.")
        else:
            explanations.append("Your depression score appears within the normal range.")
            explanations.append("Continuing to engage in meaningful activities supports mental wellbeing.")
            explanations.append("Regular mood check-ins can help maintain emotional balance.")

        if anxiety >= 4:
            explanations.append("High anxiety score - relaxation techniques or speaking to a counselor may help.")
            explanations.append("For acute anxiety, grounding techniques like 5-4-3-2-1 can provide immediate relief.")
            explanations.append("Consider limiting caffeine and creating predictable routines to reduce anxiety triggers.")
        elif anxiety >= 2:
            explanations.append("Moderate anxiety score - try to manage your triggers and seek support if needed.")
            explanations.append("Breathing exercises practiced daily can help regulate moderate anxiety responses.")
            explanations.append("Scheduling 'worry time' can contain anxious thoughts to specific periods.")
        else:
            explanations.append("Your anxiety score appears within the normal range.")
            explanations.append("Maintaining regular relaxation practices can help prevent anxiety buildup.")
            explanations.append("Being aware of physical tension can help catch early signs of anxiety.")

        return {"explanations": explanations}
    except Exception as e:
        logger.error(f"Explanation generation error: {str(e)}")
        return {"explanations": [f"Could not generate explanations: {str(e)}"]}

def home(request):
    if request.method == 'POST':
        form = MentalHealthForm(request.POST)
        if form.is_valid():
            try:
                user_data = form.cleaned_data
                logger.debug(f"Form data received: {user_data}")
                
                processed_data = preprocess_user_data(user_data)
                prediction = ada_model.predict(processed_data)

                insights = generate_user_insights(processed_data, ada_model)
                explanation = generate_explanation(prediction)

                if request.user.is_authenticated:
                    try:
                        # Convert all numeric fields to proper types
                        user_response = UserResponse(
                            user=request.user,
                            age=float(user_data['age']),
                            gender=user_data['gender'],
                            cgpa=float(user_data['cgpa']),
                            semester_credit_load=float(user_data['semester_credit_load']),
                            sleep_quality=user_data['sleep_quality'],
                            physical_activity=user_data['physical_activity'],
                            diet_quality=user_data['diet_quality'],
                            social_support=user_data['social_support'],
                            relationship_status=user_data['relationship_status'],
                            financial_stress=float(user_data['financial_stress']),
                            substance_use=user_data['substance_use'],
                            counseling_service_use=user_data['counseling_service_use'],
                            family_history=user_data['family_history'],
                            chronic_illness=user_data['chronic_illness'],
                            extracurricular_involvement=user_data['extracurricular_involvement'],
                            residence_type=user_data['residence_type']
                        )
                        
                        user_response.save()

                        prediction_obj = Prediction(
                            user_response=user_response,
                            stress_level=float(prediction[0][0]),
                            depression_score=float(prediction[0][1]),
                            anxiety_score=float(prediction[0][2]),
                        )
                        prediction_obj.save()
                    except Exception as e:
                        logger.error(f"Error saving user response: {str(e)}")
                        # Add this line to see more details about the error
                        logger.error(f"Error details: {str(e.__dict__)}")

                return render(request, 'result.html', {
                    'prediction': prediction.tolist(),
                    'insights': insights,
                    'explanation': explanation,
                    'user_data': user_data
                })

            except Exception as e:
                logger.error(f"Prediction error: {str(e)}", exc_info=True)
                return render(request, 'error.html', {
                    'error_message': "An error occurred during processing. Please check your inputs and try again."
                })
    else:
        form = MentalHealthForm()
    return render(request, 'index.html', {'form': form})

def predict_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_data = {
                'age': float(data.get('age')),
                'gender': data.get('gender'),
                'cgpa': float(data.get('cgpa')),
                'semester_credit_load': float(data.get('semester_credit_load')),
                'sleep_quality': data.get('sleep_quality'),
                'physical_activity': data.get('physical_activity'),
                'diet_quality': data.get('diet_quality'),
                'social_support': data.get('social_support'),
                'relationship_status': data.get('relationship_status'),
                'financial_stress': float(data.get('financial_stress')),
                'substance_use': data.get('substance_use'),
                'counseling_service_use': data.get('counseling_service_use'),
                'extracurricular_involvement': data.get('extracurricular_involvement'),
                'residence_type': data.get('residence_type'),
                'family_history': data.get('family_history'),
                'chronic_illness': data.get('chronic_illness'),
                'course': data.get('course'),
            }
            processed_data = preprocess_user_data(user_data)
            prediction = ada_model.predict(processed_data)

            insights = generate_user_insights(processed_data, ada_model)
            explanation = generate_explanation(prediction)

            return JsonResponse({
                'status': 'success',
                'prediction': prediction.tolist(),
                'insights': insights,
                'explanation': explanation
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        Profile.objects.create(user=request.user)
        profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form})

@login_required
def settings_view(request):
    user_form = UserUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    profile_form = ProfileForm(instance=request.user.profile)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('profile')

    context = {
        'user_form': user_form,
        'password_form': password_form,
        'profile_form': profile_form
    }
    return render(request, 'settings.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})



class blog(View):
    def get(self, request):
        context = {
            'page_title': 'MindMetrics - Mental Health Blog',
            'posts': [
                {
                    'title': '5 Effective Techniques for Managing Anxiety',
                    'category': 'Anxiety',
                    'date': 'June 15, 2023',
                    'excerpt': 'Discover practical strategies to reduce anxiety and improve your daily mental wellbeing...',
                    'image': 'images/blog1.jpg',
                    'author': {
                        'name': 'Dr. Sarah Johnson',
                        'image': 'images/author1.jpg'
                    }
                },
                # Add other posts in the same format
            ],
            'categories': [
                {'name': 'Anxiety', 'count': 12},
                {'name': 'Depression', 'count': 8},
                # Add other categories
            ],
            'popular_tags': ['self-care', 'stress', 'meditation', 'therapy', 'coping', 'habits', 'productivity', 'focus']
        }
        return render(request, 'blog.html', context)



class about(View):
    def get(self, request):
        context = {
            'page_title': 'About Us - MindMetrics',
            'team_members': [
                {
                    'name': 'Bhaskar Pal',
                    'title': 'Team Lead & ML Model Developer',
                    'bio': 'Leading the team with a vision for mental health innovation.',
                    'image': 'images/Bhaskar.jpg'
                },
                {
                    'name': 'Sreyash Mulate',
                    'title': 'ML Model Developer [ 2nd Lead ]',
                    'bio': 'Develops the AI algorithms that power our personalized recommendations.',
                    'image': 'images/sreyash.jpg'
                },
                {
                    'name': 'Sudip Kumar Patra',
                    'title': 'Backend Intregration',
                    'bio': 'Ensures seamless integration of our AI models into the platform.',
                    'image': 'images/Sudip.jpg'
                },
                {
                    'name': 'Debprasad Manna',
                    'title': 'Front-End Developer',
                    'bio': 'Designs the user interface for a smooth user experience.',
                    'image': 'images/Debprasad.jpg'
                },
                {
                    'name': 'Debanjan Bhattacharya',
                    'title': 'ML Model Developer [ 3rd Lead ]',
                    'bio': 'Works on the machine learning models that power our platform.',
                    'image': 'images/Debanjan.jpg'
                }
            ],
            'core_values': [
                {
                    'number': '01',
                    'title': 'Compassion',
                    'description': 'We approach every interaction with empathy and understanding.'
                },
                {
                    'number': '02',
                    'title': 'Innovation',
                    'description': 'Continually evolving to provide better mental health solutions.'
                },
                {
                    'number': '03',
                    'title': 'Privacy',
                    'description': 'Your data and conversations are always secure and confidential.'
                },
                {
                    'number': '04',
                    'title': 'Accessibility',
                    'description': 'Making mental health support available to everyone.'
                }
            ]
        }
        return render(request, 'about.html', context)


def contact(request):
    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        user_message = request.POST.get('message')
        
        # Basic validation
        if not all([first_name, last_name, email, user_message]):
            messages.error(request, 'Please fill all required fields!')
            return redirect('contact')
        
        # Prepare email content
        subject = f"New Contact Message from {first_name} {last_name}"
        message = f"""
        Name: {first_name} {last_name}
        Email: {email}
        Phone: {mobile}
        
        Message:
        {user_message}
        """
        
        try:
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_RECEIVING_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        
        except Exception as e:
            messages.error(request, f'Failed to send message. Error: {str(e)}')
            return redirect('contact')
    
    return render(request, 'contact.html')


