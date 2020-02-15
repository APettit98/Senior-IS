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
    CHOICES = [(1, 'Exact'), (2, 'Approximate')]
    algorithm = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)


class SingleLocationForm(forms.Form):
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter an Address'}), required=True)


LocationFormSet = formset_factory(SingleLocationForm, extra=3)


class ContactForm(forms.Form):
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

