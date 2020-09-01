from django.shortcuts import render
from lms_app.models import *
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView, ListAPIView, GenericAPIView
from rest_framework.authtoken.models import Token
from lms_app.authentication import MyAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from lms_app.serializers import *
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from functools import reduce
import operator


# Create your views here.


@authentication_classes([])
class UserLoginView(APIView):
	permission_classes = [AllowAny]
	serializer_class = UserLoginSerializer

	def post(self, request, *args, **kwargs):
		with transaction.atomic():
			if not request.data:
				# Retrun error message with 400 status
				return Response({"message": "Data is required.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			else:
				email = request.data.get('email')
				password = request.data.get('password')
				is_admin = True if request.data.get('admin') and request.data.get('admin').lower() == 'true' else False
				
				if not email:
					# Retrun error message with 400 status
					return Response({"message": "Email is required.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
				
				if not password:
					# Retrun error message with 400 status
					return Response({"message": "Password is required.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

				if is_admin:					
					user = User.objects.filter(email = email).first()
					
					if not user:
						# Retrun error message with 400 status
						return Response({"message": "This email is not registered.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    
					
					if not user.is_superuser:
						# Retrun error message with 400 status
						return Response({"message": "Given user is not Admin user.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    
				
				serializer = UserLoginSerializer(data=request.data)
				
				# check validation of serializer data
				if not serializer.is_valid(raise_exception=False):
					if serializer.errors.get('email'):  
						error_msg = ''.join(serializer.errors['email'])
						return Response({"message": error_msg,"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

					# Retrun error message with 400 status
					return Response({"message": ''.join(serializer.errors['message']),"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

				# Generating an unique token for each user
				user = User.objects.get(email = email)

				token = Token.objects.filter(user = user).first()

				if not token:
					token = Token.objects.create(user = user)
				
				user.last_login = datetime.now(tz=timezone.utc)
				user.save()

				data = serializer.data
				
				# Adding token, first name and last name to response
				data['token'] = "Token " + token.key
				data['first_name'] = user.first_name
				data['last_name'] = user.last_name
				data["mobile"] = user.mobile
				
				# Return success message with 200 status
				return Response({"message": "User is successfully logged in.", "data": data,
											"status": status.HTTP_200_OK}, status.HTTP_200_OK)



# User Logout View
class UserLogoutView(APIView):
	authentication_classes = (MyAuthentication,)

	def delete(self, request, *args, **kwargs):
		# simply delete the token to force a login
		auth_token = request.META.get("HTTP_AUTHORIZATION")
		auth_token = auth_token.split(' ')[1]
		
		token = Token.objects.filter(key = auth_token).first()
			 
		if token:
			token.delete()
		
		# Return success message with 200 status
		return Response({"message": "Logout successfully.",
									"status": status.HTTP_200_OK}, status.HTTP_200_OK)   



# Book Issue Create view
class BookIssueCreateView(CreateAPIView):
	authentication_classes = (MyAuthentication,)
	serializer_class = BookIssueDetailSerializer

	def create(self, request, *args, **kwargs):
		with transaction.atomic():
			if not request.data:
				# Retrun error message with 400 status
				return Response({"message": "Data is required.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			
			if not request.data.get('book'):
				# Retrun error message with 400 status
				return Response({"message": "Book is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			
			if not request.data.get('student'):
				# Retrun error message with 400 status
				return Response({"message": "Student is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			book_id = request.data.get('book')
			student_id = request.data.get('student')

			book = Book.objects.filter(id=book_id).first()
			student = Student.objects.filter(id=student_id).first()

			if not book:
				# Retrun error message with 400 status
				return Response({"message": "Book does not exits.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not student:
				# Retrun error message with 400 status
				return Response({"message": "Student does not exits.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			book_status = book.status
			if not book_status == "available":
					# Retrun error message with 400 status
					return Response({"message": "Book is not avilable.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			total_book_issued = student.total_book_issued
			if total_book_issued >= 3:
				# Retrun error message with 400 status
				return Response({"message": "Student does not issued more than 3 books.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			request_date = datetime.now().date()

			data = request.data.dict()
			data["request_date"] = request_date

			serializer = BookIssueDetailSerializer(data = data)

			# check validation of serializer data
			if not serializer.is_valid(raise_exception=False):
				error_msg = serializer.errors
				if serializer.errors.get('book'):
					error_msg = ''.join(serializer.errors['book'])
				if serializer.errors.get('student'):
					error_msg = ''.join(serializer.errors['student'])
				if serializer.errors.get('request_date'):
					error_msg = "Request Date is invalid."
				
				# Retrun error message with 400 status
				return Response({"message": error_msg,"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			serializer.save()

			# Retrun success message with 200 status
			return Response({"message": "Book Issue is created.", 'data': serializer.data, "status":status.HTTP_201_CREATED}, status.HTTP_201_CREATED)



# Book Issue Update view
class BookIssueUpdateView(UpdateAPIView):
	authentication_classes = (MyAuthentication,)
	serializer_class = BookIssueDetailUpdateSerializer
	lookup_field = 'id'

	def patch(self, request, *args, **kwargs):
		with transaction.atomic():

			action = request.data.get('action')
			if not action:
				# Retrun error message with 400 status
				return Response({"message": "Action is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if action.lower() != "issue" or action.lower() != "close":
				# Retrun error message with 400 status
				return Response({"message": "Invalid Action.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			staff = Staff.objects.filter(user=request.user).first()
			if not staff:
				# Retrun error message with 400 status
				return Response({"message": "This user is not staff user.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			# Fetching book issue details with given id
			book_issue_detail = BookIssueDetail.objects.filter(id = kwargs.get('id')).first()
			
			if not book_issue_detail:
				# Book Issue Detail not found
				return Response({"message": "Book Issue Detail is not found.", "status":status.HTTP_404_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

			book = book_issue_detail.book
			student = book_issue_detail.student

			if action.lower() == "issue":
			
				book.issued_quantity += 1
				book.available_quantity -= 1
				book.save()

				student.total_book_issued += 1
				student.save()

				if not book.available_quantity > 0:
					book.status = "issued"
					book.save()

				issue_date = datetime.now().date()
				data = {
					"issue_date" : issue_date,
					"staff" : staff.id,
					"status" : "issued",
				}
				message = "Book Issued Successfully."

			if action.lower() == "close":

				status = book_issue_detail.status
				if not status == "returned":
					# Retrun error message with 400 status
					return Response({"message": "Book is not returned yet.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

				student.total_book_issued -= 1
				student.save()

				data = {
					"staff" : staff.id,
					"status" : "closed",
				}
				message = "Book Return Accepted Successfully."
				
			serializer = BookIssueDetailUpdateSerializer(book_issue_detail, data = data)

			# check validation of serializer data
			if not serializer.is_valid(raise_exception=False):
				error_msg = serializer.errors			
				# Retrun error message with 400 status
				return Response({"message": error_msg,"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			serializer.save()	

			# Retrun success message with 200 status
			return Response({"message": message, "data":serializer.data, "status": status.HTTP_200_OK}, status.HTTP_200_OK)



# Book Return view
class BookReturnView(UpdateAPIView):
	authentication_classes = (MyAuthentication,)
	serializer_class = BookIssueDetailUpdateSerializer
	lookup_field = 'id'

	def patch(self, request, *args, **kwargs):
		with transaction.atomic():

			# Fetching book issue details with given id
			book_issue_detail = BookIssueDetail.objects.filter(id = kwargs.get('id')).first()
			
			if not book_issue_detail:
				# Book Issue Detail not found
				return Response({"message": "Book Issue Detail is not found.", "status":status.HTTP_404_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

			issue_date = book_issue_detail.issue_date
			return_date = datetime.now().date()

			total_days = (return_date - issue_date).days
			charge = (total_days - 15) if total_days > 15 else 0

			data = {
				"return_date" : return_date,
				"charge" : charge,
				"status" : "returned",
			}
			serializer = BookIssueDetailUpdateSerializer(book_issue_detail, data = data)

			# check validation of serializer data
			if not serializer.is_valid(raise_exception=False):
				error_msg = serializer.errors			
				# Retrun error message with 400 status
				return Response({"message": error_msg,"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			serializer.save()	

			# Retrun success message with 200 status
			return Response({"message": "Book Returned Successfully.", "data":serializer.data, "status": status.HTTP_200_OK}, status.HTTP_200_OK)



# Book Issue List view
class BookIssueListView(ListAPIView):
	authentication_classes = (MyAuthentication,)
	serializer_class = BookIssueDetailSerializer

	def get(self, request, *args, **kwargs):

		student = Student.objects.filter(user=request.user).first()
		staff = Staff.objects.filter(user=request.user).first()

		if not student and not staff:
			# Retrun error message with 400 status
			return Response({"message": "User is not found.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

		if student:
			book_issue_details = BookIssueDetail.objects.filter(student=student, status="issued")
			serializer = BookIssueDetailSerializer(book_issue_details, many=True)
			data = serializer.data

		if staff:
			students = BookIssueDetail.objects.filter(status__in=["issued", "returned"]).values_list('student', flat=True).distinct()
			data = []
			for student in students:
				book_issue_details = BookIssueDetail.objects.filter(student=student, status__in=["issued", "returned"])
				serializer = BookIssueDetailSerializer(book_issue_details, many=True)
				book_issue_details = serializer.data

				book_issue_data = {
					"total_book_issued" : len(book_issue_details),
					"book_issue_details" : book_issue_details
				}
				data.append(book_issue_data)
		
		# Retrun success message with 200 status
		return Response({"message": "Book Issue Details Retrive Successfully.", "data":data, "status": status.HTTP_200_OK}, status.HTTP_200_OK)



# Book List view
class BookListView(ListAPIView):
	authentication_classes = (MyAuthentication,)
	serializer_class = BookSerializer

	def get(self, request, *args, **kwargs):

		student = Student.objects.filter(user=request.user).first()
		staff = Staff.objects.filter(user=request.user).first()

		if not student and not staff:
			# Retrun error message with 400 status
			return Response({"message": "User is not found.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

		if student:
			search_param = request.data.get('search')
			search_param = search_param.strip() if search_param else ''

			# Fetching all book for student
			books = Book.objects.filter(status="available").order_by('-id')
			if search_param:
				q_list = []
				q_list.append(Q(name__icontains = search_param))
				q_list.append(Q(isbn__icontains = search_param))
				q_list.append(Q(author__icontains = search_param))
				q_list.append(Q(department__name__icontains = search_param))
				books = books.filter(reduce(operator.or_, q_list))

			if not books:
				# Book not found
				return Response({"message": "No Data Found.", "status":status.HTTP_404_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

			data = []
			for book in books:
				serializer = BookSerializer(book)
				book_data = serializer.data
				data.append(book_data)

		if staff:
			books = Book.objects.all()
			data = []
			for book in books:
				serializer = BookSerializer(book)
				book_data = serializer.data
				data.append(book_data)
		
		# Retrun success message with 200 status
		return Response({"message": "Book Details Retrive Successfully.", "data":data, "status": status.HTTP_200_OK}, status.HTTP_200_OK)



# Book Create view
class BookCreateView(CreateAPIView):
	authentication_classes = (MyAuthentication,)
	serializer_class = BookSerializer

	def create(self, request, *args, **kwargs):
		with transaction.atomic():
			if not request.data:
				# Retrun error message with 400 status
				return Response({"message": "Data is required.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			
			if not request.data.get('name'):
				# Retrun error message with 400 status
				return Response({"message": "Name is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			
			if not request.data.get('isbn'):
				# Retrun error message with 400 status
				return Response({"message": "Student is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not request.data.get('author'):
				# Retrun error message with 400 status
				return Response({"message": "Author is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not request.data.get('department'):
				# Retrun error message with 400 status
				return Response({"message": "Department is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not request.data.get('total_quantity'):
				# Retrun error message with 400 status
				return Response({"message": "Total Quantity is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not request.data.get('available_quantity'):
				# Retrun error message with 400 status
				return Response({"message": "Total Quantity is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			staff = Staff.objects.filter(user=request.user).first()
			if not staff:
				# Retrun error message with 400 status
				return Response({"message": "This user is not staff user.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			serializer = BookSerializer(data = request.data)

			# check validation of serializer data
			if not serializer.is_valid(raise_exception=False):
				error_msg = serializer.errors
				if serializer.errors.get('department'):
					print(serializer.errors['department'])
					error_msg = ''.join(serializer.errors['department'])
				if serializer.errors.get('name'):
					error_msg = "Name is invalid."
				if serializer.errors.get('isbn'):
					error_msg = "ISBN is invalid."
				if serializer.errors.get('author'):
					error_msg = "Author is invalid."
				if serializer.errors.get('total_quantity'):
					error_msg = "Total Quantity is invalid."
				if serializer.errors.get('available_quantity'):
					error_msg = "Available Quantity is invalid."

				# Retrun error message with 400 status
				return Response({"message": error_msg,"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			serializer.save()

			# Retrun success message with 200 status
			return Response({"message": "Book is created.", 'data': serializer.data, "status":status.HTTP_201_CREATED}, status.HTTP_201_CREATED)