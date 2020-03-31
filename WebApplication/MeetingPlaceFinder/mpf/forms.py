from django import forms
from django.forms.formsets import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, ButtonHolder
import logging

logging.basicConfig(format="%(asctime)s - %(message)s",
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger("mpfLogger")

mapbox_access_token = 'pk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazNscmN1czcwOHRsM29sanhzcm95ZmlxIn0.pRSXcRGiHLQfxj4AH1_lGg'


class EnterLocationsForm(forms.Form):
    """
    This class creates a form with a slider bar that allows the user to pick which algorithm they
    want to use based on how they prioritize speed versus accuracy
    """
    algorithm = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range', 'step': '1',
                                                                   'min': '1', 'max': '100', 'default': '50'}),
                                   label='')


class SingleLocationForm(forms.Form):
    """
    This is the template for the form that allows users to enter locations they want to meet between
    This class specifies the field for entering a single location
    """
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter an Address'}), required=True)


# Creating a formset of SingleLocationForms creates multiple within the same form
# By default it starts with 3 location fields
LocationFormSet = formset_factory(SingleLocationForm, extra=3)


class ContactForm(forms.Form):
    """
    This form is used for the contact page,
    it allows users to enter information for an email to be sent to me
    """
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': "Your Email"}), required=True)
    subject = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Subject'}), required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Message'}), required=True)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_method = 'POST'
    helper.form_show_labels = False

    helper.layout = Layout(
        Row(
            Column('email', css_class='form-group'),
            css_class='form-row'
        ),
        Row(
            Column('subject', css_class='form-group'),
            css_class='form-row'
        ),
        Row(
            Column('message', css_class='form-group'),
            css_class='form-row'
        ),
        ButtonHolder(
            Submit('submit', 'Submit', css_class='btn btn-primary')
        )
    )

