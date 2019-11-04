from django import forms
from crispy_forms.helper import FormHelper, reverse
from crispy_forms.layout import Submit, Layout, Field, Row, Column
from crispy_forms.bootstrap import FormActions


class EnterLocationsForm(forms.Form):
    template_name = 'mpf/index.html'
    location1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 1'}))
    location2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 2'}))
    location3 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 3'}))

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
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
        FormActions(
            Submit('start_search', 'Go', css_class='btn btn-primary btn-large btn-block')
        )
    )

