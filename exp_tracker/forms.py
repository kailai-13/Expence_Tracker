from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    long_term = forms.BooleanField(required=False)

    class Meta:
        model = Expense
        fields = ['name', 'amount', 'interest_rate', 'date', 'end_date', 'long_term']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'long_term': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        long_term = cleaned_data.get('long_term')
        start_date = cleaned_data.get('date')
        
        # Check if long-term is selected
        if long_term:
            interest_rate = cleaned_data.get('interest_rate')
            end_date = cleaned_data.get('end_date')
            amount = cleaned_data.get('amount')

            # Validate that interest rate and end date are provided if long-term is checked
            if not interest_rate or not end_date:
                raise forms.ValidationError("Interest rate and end date must be provided for long-term expenses.")

            cleaned_data['long_term'] = True
        else:
            # If not long-term, reset these fields
            cleaned_data['end_date'] = None
            cleaned_data['interest_rate'] = None

        return cleaned_data
    