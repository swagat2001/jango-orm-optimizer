from django.core.management.base import BaseCommand
from core.models import Author, Book, Category

class Command(BaseCommand):
    help = "Demonstrate and optimize Django ORM queries"

    def handle(self, *args, **options):
        # Ensure there is data to work with
        if Author.objects.count() == 0 or Category.objects.count() == 0:
            self.stdout.write(self.style.WARNING("No data found. Creating sample data..."))
            authors = [Author.objects.create(name=f"Author {i}") for i in range(1, 6)]
            categories = [Category.objects.create(name=f"Category {i}") for i in range(1, 6)]
            for author in authors:
                for j in range(1, 21):
                    book = Book.objects.create(title=f"Book {j} by {author.name}", author=author)
                    # Assign random categories to each book
                    book.categories.set(categories[j % len(categories):] + categories[:j % len(categories)])
            self.stdout.write(self.style.SUCCESS("Sample data created."))

        # SLOW QUERY (N+1 problem)
        import time
        self.stdout.write(self.style.NOTICE("Running slow query (N+1 problem)..."))
        start = time.time()
        books = Book.objects.all()
        for book in books:
            author_name = book.author.name  # Triggers a query per book
        duration = time.time() - start
        self.stdout.write(self.style.ERROR(f"Slow query took {duration:.4f} seconds for {books.count()} books."))

        # OPTIMIZED QUERY (using select_related)
        self.stdout.write(self.style.NOTICE("Running optimized query (using select_related)..."))
        start = time.time()
        books = Book.objects.select_related('author').all()
        for book in books:
            author_name = book.author.name  # No extra queries
        duration = time.time() - start
        self.stdout.write(self.style.SUCCESS(f"Optimized query took {duration:.4f} seconds for {books.count()} books."))

        # SLOW QUERY (N+1 problem with ManyToMany)
        self.stdout.write(self.style.NOTICE("Running slow query (N+1 problem) for ManyToMany (categories)..."))
        start = time.time()
        books = Book.objects.all()
        for book in books:
            category_names = [cat.name for cat in book.categories.all()]  # Triggers a query per book
        duration = time.time() - start
        self.stdout.write(self.style.ERROR(f"Slow ManyToMany query took {duration:.4f} seconds for {books.count()} books."))

        # OPTIMIZED QUERY (using prefetch_related)
        self.stdout.write(self.style.NOTICE("Running optimized query (using prefetch_related for categories)..."))
        start = time.time()
        books = Book.objects.prefetch_related('categories').all()
        for book in books:
            category_names = [cat.name for cat in book.categories.all()]  # No extra queries
        duration = time.time() - start
        self.stdout.write(self.style.SUCCESS(f"Optimized ManyToMany query took {duration:.4f} seconds for {books.count()} books."))
