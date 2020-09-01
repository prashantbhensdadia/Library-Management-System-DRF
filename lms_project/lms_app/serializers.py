# from django.db.models import Q
# from rest_framework.serializers import ModelSerializer, \
# 									   ValidationError, \
# 									   EmailField
from rest_framework import serializers
from lms_app.models import *
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED


# from django.conf import settings




# User LOGIN Serializer
class UserLoginSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(label = 'Email')

	class Meta:
		model = User
		fields = ('email','password','id')
		extra_kwargs = {
						'password': {'write_only':True}
						}
						
	def validate(self, data):
		user_obj = None
		response = {}
		email =  data.get('email', None)
		password =  data.get('password', None)
		# Fetching user with email
		user = User.objects.filter(email=email).first()
		if user:
			# User exists
			user_obj = user
		else:
			# User does not exist
			response['message'] = "This email is not registered."
			raise serializers.ValidationError(response)
		
		if user_obj:
			# Checking password is correct or not
			if not user_obj.check_password(password):
				# Incorrect password
				response['message'] = "Password is incorrect."
				raise serializers.ValidationError(response)
  
		data['id'] = user_obj.id
		return data


class BookIssueDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = BookIssueDetail
		fields = ('id', 'book', 'request_date', 'issue_date', 'return_date', 'student', 'staff', 'charge', 'status')


class BookIssueDetailUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = BookIssueDetail
		fields = ('id', 'issue_date', 'return_date', 'student', 'staff', 'charge', 'status')


class BookSerializer(serializers.ModelSerializer):
	department_name = serializers.ReadOnlyField(source='department.name')

	class Meta:
		model = Book
		fields = ('id', 'name', 'isbn', 'author', 'department', 'department_name', 'total_quantity', 'issued_quantity', 'available_quantity', 'status')