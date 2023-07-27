from rest_framework import generics
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import TextBlock, User
from .serializers import TextBlockSerializer, UserSerializer
from chatbot.openai_api import main

@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'user_id': f"{serializer.data['id']}"})
        return JsonResponse(serializer.errors, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(['POST'])
def create_text(request):
    if request.method == 'POST':
        serializer = TextBlockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = main(serializer.data['user'], serializer.data['grade'])
            user = User.objects.filter(id=serializer.data['user'])[0]
            gpt_message = TextBlock(user=user, is_user=False, text=response, grade=serializer.data['grade'])
            gpt_message.save()
            return JsonResponse({'message': f"{response}"})
        return JsonResponse(serializer.errors, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)