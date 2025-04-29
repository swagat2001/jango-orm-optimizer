from django.core.management.base import BaseCommand
from core.models import Author, Book

class Command(BaseCommand):
    help = "Demonstrate and optimize Django ORM queries"

    def handle(self, *args, **options):
        # Ensure there is data to work with
        if Author.objects.count() == 0:
            self.stdout.write(self.style.WARNING("No data found. Creating sample data..."))
            authors = [Author.objects.create(name=f"Author {i}") for i in range(1, 6)]
            for author in authors:
                for j in range(1, 21):
                    Book.objects.create(title=f"Book {j} by {author.name}", author=author)
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
