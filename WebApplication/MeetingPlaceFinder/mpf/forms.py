from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, ButtonHolder, Button


class EnterLocationsForm(forms.Form):
    template_name = 'mpf/index.html'
    location1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 1'}))
    location2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 2'}))
    location3 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 3'}))
    extra_location_count = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'count'}), initial=0)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_method = 'POST'
    helper.form_show_labels = False
    helper.layout = Layout(
        Row(
            Column('location1', css_class='form-group'),
            css_class='form-row'
        ),
        Row(
            Column('location2', css_class='form-group'),
            css_class='form-row'
        ),
        Row(
            Column('location3', css_class='form-group'),
            css_class='form-row'
        ),
        Row(
            Column('extra_location_count'),
        ),
        ButtonHolder(
            Button('submit', 'Go', css_class='btn btn-primary'),
            Button('add', '+', css_class="btn btn-success"),
            css_id="button-row",
        )
    )

    def __init__(self, *args, **kwargs):
        extra_locations = kwargs.pop('extra', 0)

        super().__init__(*args, **kwargs)
        self.fields['extra_location_count'].initial = extra_locations

        for index in range(int(extra_locations)):
            self.fields['extra_location_{}'.format(index)] = forms.CharField(
                widget=forms.TextInput(attrs={'placeholder': 'Address {}'.format(str(3 + int(extra_locations)))})
            )


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


