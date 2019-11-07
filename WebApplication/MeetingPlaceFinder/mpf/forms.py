from django import forms
from crispy_forms.helper import FormHelper, reverse
from crispy_forms.layout import Submit, Layout, Field, Row, Column, Div, ButtonHolder
from crispy_forms.bootstrap import FormActions


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
            Column('extra_location_count'),
            css_class='form-row'
        ),
        ButtonHolder(
            Submit('submit', 'Go', css_class='btn btn-primary'),
            Submit('add', '+', css_class="btn btn-success"),
            css_id="button-row",
        )
    )

    # helper.all().wrap(Div, css_class="form-group-row")
    # helper.all().wrap_together(Div, css_class="form-group")

    def __init__(self, *args, **kwargs):
        print(kwargs)
        extra_locations = kwargs.pop('extra', 0)
        print(extra_locations)

        super().__init__(*args, **kwargs)
        self.fields['extra_location_count'].initial = extra_locations

        for index in range(int(extra_locations)):
            self.fields['extra_location_{}'.format(index)] = forms.CharField(
                widget=forms.TextInput(attrs={'placeholder': 'Address {}'.format(str(3 + int(extra_locations)))})
            )


