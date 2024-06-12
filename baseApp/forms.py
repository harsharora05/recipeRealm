from django import forms
from baseApp.models import recipe
from tinymce.widgets import TinyMCE




class RecipeForm(forms.ModelForm):
    class Meta:
        model = recipe
        fields = ("category","meal_prefrence","title","ingredients","steps","recipe_photo")

        widgets= {
            'category' : forms.Select(attrs={'class':'form-control'}),
            'meal_prefrence' : forms.Select(attrs={'class':'form-control'}),
            'title' : forms.TextInput(attrs={'class':'form-control'}),
            'ingredients' : forms.Textarea(attrs={'class':'form-control','rows':'4','placeholder':"Just give one space after every Ingredient. "}),
            'steps' : forms.Textarea(attrs={'class':'form-control','rows':'4','placeholder':"Don't give extra gap between steps...Just give one space after every step. "}),
            'recipe_photo' : forms.FileInput(attrs={'class':'form-control'}),
        }



