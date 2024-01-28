from django import forms

from django.core.validators import MinValueValidator

class CreateForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(widget=forms.Textarea, label="Description", required=False)
    price = forms.IntegerField(label="Initial Price", validators=[MinValueValidator(1)])
    img_url = forms.URLField(label="Img URL(optional)", required=False)
    
    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

# class BidForm(forms.Form):
#     bid = forms.IntegerField(validators=[MinValueValidator(1)])

#     def __init__(self, *args, **kwargs):
#         super(BidForm, self).__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             visible.field.widget.attrs['class'] = 'form-control'

class AddCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, label="Add a comment")

    def __init__(self, *args, **kwargs):
        super(AddCommentForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
