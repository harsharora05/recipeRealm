from django.shortcuts import render,HttpResponse,HttpResponseRedirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from .models import recipe
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import date,timedelta
import requests
from .forms import RecipeForm



# Create your views here.

def index(request):

        categories = recipe._meta.get_field('category').choices
        famousRecipies  =  recipe.objects.filter(famous = True) 

        currDate = date.today()
        yesDate = currDate - timedelta(days=1)
        
        response = requests.get(f'https://newsapi.org/v2/top-headlines?q=health&pageSize=1&from={yesDate}&to={currDate}&sortBy=popularity&language=en&apiKey=d08679a5e53045ed943cf82c5a104af7')

        data = response.json()
               
        # print(data['articles'])
        
        context={"categories":categories,
                 "famousRecipies":famousRecipies,
                 "data":data['articles']
        }


        return render(request,'AppTemplates/home.html',context)


        
def categoryPage(request,slug):

        # for navbar recipes 
        categories = recipe._meta.get_field('category').choices

        # getting recipies using slug
        recipies = recipe.objects.filter(category = slug,active =True)

        # for displaying heading on category page
        str= slug.lower()
        str_new = str[0].upper()
        catTitle= str_new+str[1:]


        context={"recipies":recipies,
                 "categories":categories,
                 "catTitle":catTitle}

        return render(request,'AppTemplates/categories.html',context)







def searchQuery(request):
        # for navbar recipes 
        categories = recipe._meta.get_field('category').choices
        
        query = str(request.GET.get("searchQ"))
        if len(query) > 40:
                Allresult = recipe.objects.none()
        else:
                Alltitle=recipe.objects.filter(title__icontains = str(query) , active = True)
                Allcategory=recipe.objects.filter(category__icontains = str(query) ,active = True)
                Allmeal_prefrence=recipe.objects.filter(meal_prefrence__icontains = str(query),active = True)
                semiResult = Alltitle.union(Allcategory)
                Allresult=Allmeal_prefrence.union(semiResult)
        
        if Allresult.count() == 0:
                messages.warning(request,"Query not found")

        return render(request,"AppTemplates/search.html", context={"categories":categories,"Allresult":Allresult,"query":query})





def explore(request,id):
          # for navbar recipes 
        categories = recipe._meta.get_field('category').choices


        Recipe = get_object_or_404(recipe,id=id,active = True)

        return render (request,"AppTemplates/explore.html" ,context = {"Recipe":Recipe,"categories":categories})

def about(request):
          # for navbar categories 
        categories = recipe._meta.get_field('category').choices
        return render (request,"AppTemplates/about.html" ,context = {"categories":categories})




@login_required
def yourRecipies(request):
          # for navbar categories 
        categories=recipe._meta.get_field('category').choices
        
        ownerRecipes = recipe.objects.filter(recipeOwner = request.user )

        context= {"categories":categories,
                  "ownerRecipes":ownerRecipes}
        return render(request,"AppTemplates/yourRecipies.html",context)


@login_required
def deleteRecipe(request,id):
        if request.method=='POST':
                recipeD  = recipe.objects.filter(id=id)
                recipeD.delete()

                messages.success(request,"Recipe Successfully Deleted")
                return HttpResponseRedirect(reverse('index'))


@login_required
def updateRecipe(request,id):
        # for navbar categories 
        categories = recipe._meta.get_field('category').choices
        # passing this recipe object only to access id
        recipeobj = get_object_or_404(recipe,id=id)

        if request.method == 'GET':
                RecipeObject = recipe.objects.get(id=id)
                UpdateForm = RecipeForm({
                        'category':RecipeObject.category,
                        'meal_prefrence': RecipeObject.meal_prefrence,
                        'title':RecipeObject.title,
                        'ingredients':RecipeObject.ingredients,
                        'steps':RecipeObject.steps,
                        'recipe_photo':RecipeObject.recipe_photo
                })
        if request.method =='POST':
                # last object delete
                recipeD  = recipe.objects.filter(id=id)
                recipeD.delete()
                recipeform =RecipeForm(data = request.POST , files = request.FILES)

                if recipeform.is_valid():
                      form = recipeform.save(commit = False)
                      form.recipeOwner = request.user
                      form.ingredients_HTML =form.ingredients
                      form.steps_HTML =form.steps
                      form.active = False 
                      form.save()

                      messages.success(request,"Updated sucessfully....It will be live within 24 hours")
                      return HttpResponseRedirect(reverse('index'))

        return render(request,'AppTemplates/updateRecipe.html',context={"UpdateForm":UpdateForm , "recipeobj" :recipeobj,"categories":categories})



@login_required
def addRecipe(request):
        # for navbar recipes 
        categories = recipe._meta.get_field('category').choices

        if request.method == 'POST':
                Rform = RecipeForm(data=request.POST, files=request.FILES)
                if Rform.is_valid():
                        recipeForm = Rform.save(commit=False)
                        recipeForm.recipeOwner=request.user
                        recipeForm.ingredients_HTML =recipeForm.ingredients
                        recipeForm.steps_HTML =recipeForm.steps
                        recipeForm.save()
                   
                   
                        messages.success(request,'sucessfully added....Recipe will be live With in 24Hours')
                        return HttpResponseRedirect(reverse('index'))
                else:
                        print(Rform.errors)
        else:
                Rform = RecipeForm()
        

    
        return render(request,'AppTemplates/addRecipe.html',context={'Rform':Rform,'categories':categories} )



def userRegisteration(request):
        if request.method == "POST":
                fname = request.POST.get("fname")
                lname = request.POST.get("lname")
                uname = request.POST.get("username")
                email = request.POST.get("email")
                password = request.POST.get("password")
                confirmPassword= request.POST.get("confirmPassword")
        
                if password != confirmPassword :
                        messages.warning(request, "Password Not Equal To Confirm Password")
                        return HttpResponseRedirect(reverse('index'))
                if  len(password) < 8:
                        messages.warning(request, "Password less than 8 charracter")
                        return HttpResponseRedirect(reverse('index'))
                if User.objects.filter(username=uname).first():
                        messages.warning(request, "Try another UserName")
                        return HttpResponseRedirect(reverse('index'))
                if User.objects.filter(email=email).first():
                        messages.warning(request, "account with this email is already there")
                        return HttpResponseRedirect(reverse('index'))

                else:
                        user = User.objects.create_user(first_name = fname,last_name = lname,username = uname, email = email, password = password)
                        user.save()
                        
                        messages.success(request, "User Created... Please Login!!")

                        return HttpResponseRedirect(reverse('index'))
                        
                
        else:

                messages.warning(request, "User Created... Please Login!!")
                return HttpResponseRedirect(reverse('index'))


    
def user_login(request):
        if request.method == 'POST':
                username = request.POST['username']
                password = request.POST['password']

                user = authenticate(request,username = username, password = password)
                if user is not None:
                        login(request,user)
                        messages.success(request,"Login Successfull")
                        return HttpResponseRedirect(reverse('index'))
                else:
                        messages.warning(request,"Login Failed,Try Again")
                        return HttpResponseRedirect(reverse('index'))
        else:
                return HttpResponse('error-404')


@login_required
def userLogout(request):
        logout(request)
        messages.success(request,"Logout Successfully")
        return HttpResponseRedirect(reverse('index'))


