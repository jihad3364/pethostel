from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from datetime import date
from django.db.models import Q
from .forms import EmployeeForm, PetForm
from .models import EmployeeReg, PetRegistration, UserProfile, Room, Booking


def home(request):
        pets = PetRegistration.objects.filter(owner_id=request.user.id)
        return render(request, 'home.html',{'pets':pets})

def services(request):
    return render(request, 'services.html')

def add_room(request):
    if request.method=='POST':
        type = request.POST['category']
        count = int(request.POST['count'])
        room = Room.objects.filter(category=type)
        for r in room:
            r.total_rooms += count
            r.save()
        return redirect('room')

    return render(request,'add_room.html')
def remove_room(request):
    if request.method=='POST':
        type = request.POST['category']
        count = int(request.POST['count'])
        room = Room.objects.filter(category=type)
        for r in room:
            r.total_rooms -= count
            r.save()
        return redirect('room')
    return render(request,'remove_room.html')

def room_info(request):
    room = Room.objects.all()
    bookings = Booking.objects.all()
    return render(request,'room.html',{'room':room, 'bookings':bookings})

def pricechange(request):
    if request.method=='POST':
        type = request.POST['category']
        new_price = int(request.POST['price'])
        room = Room.objects.filter(category=type)
        for r in room:
            r.price = new_price
            r.save()
        return redirect('room')
    return render(request,'price_change.html')
#=============authentication part===============

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return render(request, 'login.html')
    elif request.user.is_authenticated:
        return redirect('/')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

#-------------------Employees-------------------
def employee_list(request):
      employees = EmployeeReg.objects.all()
      return render(request, 'employee_list.html',{'employees':employees})

def employee_add(request):
        if request.method == 'POST':
            form = EmployeeForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('employee_list')
        else:
            form = EmployeeForm
        return render(request, 'employee_add.html', {'form': form})

def remove_employee(request, employee_id):
    employee = EmployeeReg.objects.get(pk=employee_id)
    employee.is_active = False
    employee.save()
    return redirect('employee_list')

#================Customers===============

def register(request):
    if request.method == 'POST':
        fname = request.POST ['fname']
        lname = request.POST ['lname']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST ['phone']
        birth = request.POST ['birth']
        address = request.POST ['address']
        password = request.POST['passwrd']
        if User.objects.filter(username=username).exists():
            messages.info(request,'Usrname already in use')
            return render(request,'register.html')
        else:
            user = User.objects.create_user(first_name = fname, last_name = lname, email=email,password=password,username=username)
            profile = UserProfile.objects.create(user=user, phone_number=phone, birthdate=birth, address=address)

            #login
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('/')

    elif request.user.is_authenticated:
        return redirect('/')
    return render(request,'register.html')

def customers(request):
    users = User.objects.select_related('userprofile').all()
    pets = PetRegistration.objects.all()
    bookings = Booking.objects.all()
    return render(request,'customers.html', {'users':users, 'pets':pets, 'bookings':bookings})

def pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            return redirect('/')
    else:
        form = PetForm
    return render(request,'petregister.html',{'form':form})

#=======management==============
def search(request):
    return render(request,'search.html')

def confirm_booking(request):
    if request.method == 'POST':
        checkin = request.POST['checkin']
        checkout = request.POST['checkout']
        petcount = int(request.POST['petcount'])
        category = request.POST['category']
        cost = request.POST['cost']
        pets = request.POST.getlist('pets')
        if len(pets)>petcount:
            messages.info(request, 'You used invalid pet numbers, Please try again')
            return redirect('search')

    booking =  Booking.objects.create(check_in_date=checkin, check_out_date=checkout, number_of_pets=petcount, room_category = category, cost=cost,  customer=request.user, pets=pets)
    booking.save()
    return render(request,'success.html')

def availability(request):
    if request.method=='POST':
        available = True
        checkin = request.POST['check_in']
        checkout = request.POST['check_out']
        petnumber = int(request.POST['pet_number'])
        category = request.POST['room_type']

      #====booking dates validity check======
        if checkout<checkin or checkin<str(date.today()):
            messages.info(request, 'Invalid date input')
            return redirect('search')

        booked_rooms = Booking.objects.filter(room_category=category)
        categ = Room.objects.filter(category=category)

        #if booked room exist for same category
        if booked_rooms:
            total_pets = 0
            overlapping_bookings = Booking.objects.filter(Q(check_in_date__lte=checkout, check_out_date__gte=checkin, room_category=category))
            if overlapping_bookings.exists():
                for i in overlapping_bookings:
                    total_pets += i.number_of_pets
            for r in categ:
                if total_pets + petnumber <= (r.capacity * r.total_rooms):
                    pass
                else:
                    available = False
    #============end of existing bookings==============
        if available:
            # duration and price calculation
            day_count = int(checkout[-2:])-int(checkin[-2:])+1
            month_count = int(checkout[-5:-3])-int(checkin[-5:-3])
            year_count =  int(checkout[:4])-int(checkin[0:4])
            if year_count>0:
                month_count += 12 * year_count

            if month_count>0 and day_count>0:
                day_count += month_count * 30
            elif month_count>0 and day_count<0:
                day_count = ((month_count-1)*30) + (30+day_count)

            for room in categ:
              room_price = room.price * petnumber * day_count
            context = {
                'checkin':checkin,
                'checkout':checkout,
                'petcount':petnumber,
                'category':category,
                'pets': PetRegistration.objects.filter(owner_id = request.user.id),
                'cost': room_price,
            }

            return render(request,'booking.html',context)
        else:
            messages.info(request,'Not available, Please try a different category or date')
            return redirect('search')

def bookinglist(request):
    bookings = Booking.objects.order_by('-id')
    return render(request, 'booking_info.html',{'bookings':bookings})
