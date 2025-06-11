from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Profile
from django.core.validators import EmailValidator, RegexValidator


class MentalHealthForm(forms.Form):
    age = forms.IntegerField(
        label='Age',
        widget=forms.NumberInput(attrs={'placeholder': 'Enter your age (e.g., 20)'}),
        validators=[MinValueValidator(10), MaxValueValidator(100)]
    )
    
    GENDER_CHOICES = [
        ('', '-- Select Gender --'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    ]
    gender = forms.ChoiceField(
        label='Gender',
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    COURSE_CHOICES = [
        ('', '-- Select Course --'),
        ('Engineering', 'Engineering'),
        ('Business', 'Business'),
        ('Computer', 'Computer Science'),
        ('Law', 'Law'),
        ('Medical', 'Medical'),
        ('Other', 'Other'),
    ]
    course = forms.ChoiceField(
        label='Course',
        choices=COURSE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}))
    
    cgpa = forms.DecimalField(
        label='CGPA/GPA',
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter CGPA (Between 1.0-4.0)',
            'step': '0.01'
        }),
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
    )
    
    semester_credit_load = forms.IntegerField(
        label='Semester Credit Load',
        widget=forms.NumberInput(attrs={'placeholder': 'Enter credits (Between, 15-30)'}),
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    
    SLEEP_QUALITY_CHOICES = [
        ('', '-- Select Sleep Quality --'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
    ]
    sleep_quality = forms.ChoiceField(
        label='Sleep Quality',
        choices=SLEEP_QUALITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    PHYSICAL_ACTIVITY_CHOICES = [
        ('', '-- Select Physical Activity --'),
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High'),
    ]
    physical_activity = forms.ChoiceField(
        label='Physical Activity',
        choices=PHYSICAL_ACTIVITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    DIET_QUALITY_CHOICES = [
        ('', '-- Select Diet Quality --'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
    ]
    diet_quality = forms.ChoiceField(
        label='Diet Quality',
        choices=DIET_QUALITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    SOCIAL_SUPPORT_CHOICES = [
        ('', '-- Select Social Support --'),
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High'),
    ]
    social_support = forms.ChoiceField(
        label='Social Support',
        choices=SOCIAL_SUPPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    RELATIONSHIP_STATUS_CHOICES = [
        ('', '-- Select Relationship Status --'),
        ('Single', 'Single'),
        ('In a relationship', 'In a relationship'),
        ('Married', 'Married'),
    ]
    relationship_status = forms.ChoiceField(
        label='Relationship Status',
        choices=RELATIONSHIP_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    financial_stress = forms.DecimalField(
        label='Financial Stress',
        max_digits=3,
        decimal_places=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Rate 1-5 (1 = Highest)',
            'step': '0.1'
        }),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    SUBSTANCE_USE_CHOICES = [
        ('', '-- Select Substance Use --'),
        ('Never', 'Never'),
        ('Occasionally', 'Occasionally'),
        ('Frequently', 'Frequently'),
    ]
    substance_use = forms.ChoiceField(
        label='Substance Use',
        choices=SUBSTANCE_USE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    COUNSELING_CHOICES = [
        ('', '-- Select Counseling Usage --'),
        ('Never', 'Never'),
        ('Occasionally', 'Occasionally'),
        ('Frequently', 'Frequently'),
    ]
    counseling_service_use = forms.ChoiceField(
        label='Counseling Service Usage',
        choices=COUNSELING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    FAMILY_HISTORY_CHOICES = [
        ('', '-- Select Family History --'),
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    family_history = forms.ChoiceField(
        label='Family History of Mental Health Issues',
        choices=FAMILY_HISTORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    CHRONIC_ILLNESS_CHOICES = [
        ('', '-- Select Chronic Illness --'),
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    chronic_illness = forms.ChoiceField(
        label='Chronic Illness',
        choices=CHRONIC_ILLNESS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    EXTRACURRICULAR_CHOICES = [
        ('', '-- Select Involvement Level --'),
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High'),
    ]
    extracurricular_involvement = forms.ChoiceField(
        label='Extracurricular Involvement',
        choices=EXTRACURRICULAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    RESIDENCE_CHOICES = [
        ('', '-- Select Residence Type --'),
        ('On-Campus', 'On-Campus'),
        ('Off-Campus', 'Off-Campus'),
        ('With Family', 'With Family'),
    ]
    residence_type = forms.ChoiceField(
        label='Residence Type',
        choices=RESIDENCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio', 'location']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_image'
            }),
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your location'
            }),
        }
        labels = {
            'image': 'Profile Picture',
            'bio': 'Biography',
            'location': 'Location'
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
        }


        
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')



class ContactForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'required': 'required'
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'required': 'required'
        })
    )
    
    email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': 'required'
        })
    )
    
    mobile = forms.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 12 digits allowed."
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your mobile number',
            'required': 'required'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your message here...',
            'rows': 4,
            'required': 'required'
        })
    )

