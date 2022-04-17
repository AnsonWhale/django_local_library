import datetime

from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from catalog.forms import RenewBookForm

# Create your views here.
def index(request):
    """View function for home page of site"""

    #Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    #Availible books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact ='a').count()

    #The 'all()' is implied by default
    num_authors = Author.objects.count()

    #number of books with the word Jimmy
    num_books_include_jimmy = Book.objects.filter(title__icontains = 'Jimmy').count()

    #number of visits to this view, as counted in the session variable
    num_visits = request.session.get('num_visits',0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_books_include_jimmy': num_books_include_jimmy,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request,'index.html',context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    #context_object_name = 'book_list'
    #queryset = Book.objects.filter(title__icontains='Jimmy')[:5]
    #template_name = 'books/my_arbitrary_template_name_list.html'

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    queryset = Author.objects.order_by('first_name')
    paginate_by = 2

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllLoanedBooksListView(PermissionRequiredMixin,generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned',raise_exception=True)
def renew_book_librarian(request,pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin,CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin,DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

    permission_required = 'catalog.can_mark_returned'

class BookCreate(PermissionRequiredMixin,CreateView):
    model = Book
    fields = ['title','author','summary','isbn','genre','language']

    permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin,CreateView):
    model = Book
    fields = ['title','author','summary','isbn','genre','language']

    permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin,CreateView):
    model = Book
    success_url = reverse_lazy('books')

    permission_required = 'catalog.can_mark_returned'