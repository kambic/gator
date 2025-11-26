from django.shortcuts import render

def tube(request):
    return render(request, 'tube/tube.html')
