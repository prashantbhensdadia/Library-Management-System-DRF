from django.urls import path
from lms_app.views import *
from django.conf import settings


urlpatterns = [
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', UserLogoutView.as_view(), name='logout'), 
    path('book_issue/create', BookIssueCreateView.as_view(), name='book_issue_create'), 
    path('book_issue/update/<id>', BookIssueUpdateView.as_view(), name='book_issue_update'),  
    path('book_issue/return/<id>', BookReturnView.as_view(), name='book_issue_return'),   
    path('book_issue/list', BookIssueListView.as_view(), name='book_issue_list'), 
    path('book/create', BookCreateView.as_view(), name='book_create'), 
    path('book/list', BookListView.as_view(), name='book_list'), 

]
