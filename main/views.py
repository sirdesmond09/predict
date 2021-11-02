from rest_framework.decorators import api_view, authentication_classes, permission_classes, schema
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Post
from .serializers import PostSerializer
from drf_yasg.utils import swagger_auto_schema


OWNER_ONLY_METHODS = ['PUT', 'PATCH', 'DELETE']


@swagger_auto_schema(methods=['POST'], request_body=PostSerializer())
@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def posts(request):
    if request.method == 'GET':
        obj = Post.objects.filter(is_active=True).order_by('-date_created')
        serializer = PostSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
@swagger_auto_schema(methods=['PATCH', 'DELETE'], request_body=PostSerializer())
@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request, post_id):
    
    try:
        post = Post.objects.get(id=post_id, is_active=True)
    except Post.DoesNotExist:
        return Response({'error':"Post with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method in OWNER_ONLY_METHODS and post.user != request.user:
        raise PermissionDenied(detail="You do not have the permission to edit or delete this post as it does not belong to you")


    if request.method == 'GET':
        
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            if 'likes' in serializer.validated_data.keys():
                raise ValidationError(detail="This feature cannot be manually edited.")
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        post.delete()
        return Response({'message':'successful'},  status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, is_active=True)
    except Post.DoesNotExist:
        return Response({'error':"Post with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        post.likes+=1
        post.save()
        return Response({'message':'Liked succesful'}, status=status.HTTP_200_OK)
    