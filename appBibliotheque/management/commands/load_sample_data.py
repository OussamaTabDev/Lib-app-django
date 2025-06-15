# appBibliotheque/management/commands/load_sample_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
from accounts.models import Utilisateur
from appBibliotheque.models import Categorie, Livre, Exemplaire, Emprunter, Reservation, Notification
import os

class Command(BaseCommand):
    help = 'Load sample data for the library management system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to load sample data...'))

        # 1. Create Categories
        self.stdout.write('Creating categories...')
        categories_data = [
            ('Fiction', 'Romans et nouvelles de fiction', 'fiction'),
            ('Science-Fiction', 'Livres de science-fiction et fantasy', 'science-fiction'),
            ('Histoire', 'Livres d\'histoire et biographies historiques', 'histoire'),
            ('Sciences', 'Livres scientifiques et techniques', 'sciences'),
            ('Philosophie', 'Ouvrages philosophiques et essais', 'philosophie'),
            ('Littérature classique', 'Grands classiques de la littérature', 'litterature-classique'),
            ('Jeunesse', 'Livres pour enfants et adolescents', 'jeunesse'),
            ('Biographie', 'Biographies et autobiographies', 'biographie'),
        ]

        categories = {}
        for nom, description, slug in categories_data:
            cat, created = Categorie.objects.get_or_create(
                nom=nom,
                defaults={'description': description, 'slug': slug}
            )
            categories[nom] = cat
            if created:
                self.stdout.write(f'  Created category: {nom}')

        # 2. Create Books with placeholder images
        self.stdout.write('Creating books...')
        books_data = [
            {
                'auteur': 'Victor Hugo',
                'titre': 'Les Misérables',
                'isbn': '978-2-07-040010-1',
                'description': 'Chef-d\'œuvre de la littérature française du XIXe siècle...',
                'date_publication': datetime(1862, 1, 1).date(),
                'categories': ['Fiction', 'Littérature classique']
            },
            {
                'auteur': 'Jules Verne',
                'titre': 'Vingt mille lieues sous les mers',
                'isbn': '978-2-07-040020-0',
                'description': 'Aventure extraordinaire du capitaine Nemo...',
                'date_publication': datetime(1870, 1, 1).date(),
                'categories': ['Science-Fiction', 'Jeunesse']
            },
            {
                'auteur': 'Albert Camus',
                'titre': 'L\'Étranger',
                'isbn': '978-2-07-036002-1',
                'description': 'Roman existentialiste racontant l\'histoire de Meursault...',
                'date_publication': datetime(1942, 1, 1).date(),
                'categories': ['Fiction', 'Philosophie']
            },
            {
                'auteur': 'Antoine de Saint-Exupéry',
                'titre': 'Le Petit Prince',
                'isbn': '978-2-07-040150-4',
                'description': 'Conte poétique et philosophique...',
                'date_publication': datetime(1943, 1, 1).date(),
                'categories': ['Jeunesse', 'Philosophie']
            },
            {
                'auteur': 'Molière',
                'titre': 'Le Malade imaginaire',
                'isbn': '978-2-07-038001-2',
                'description': 'Dernière comédie de Molière...',
                'date_publication': datetime(1673, 1, 1).date(),
                'categories': ['Littérature classique']
            },
            {
                'auteur': 'Émile Zola',
                'titre': 'Germinal',
                'isbn': '978-2-07-037025-7',
                'description': 'Roman naturaliste décrivant les conditions de vie des mineurs...',
                'date_publication': datetime(1885, 1, 1).date(),
                'categories': ['Fiction', 'Histoire']
            },
            {
                'auteur': 'Alexandre Dumas',
                'titre': 'Les Trois Mousquetaires',
                'isbn': '978-2-07-045010-6',
                'description': 'Roman d\'aventures suivant D\'Artagnan...',
                'date_publication': datetime(1844, 1, 1).date(),
                'categories': ['Fiction', 'Histoire']
            },
            {
                'auteur': 'Voltaire',
                'titre': 'Candide',
                'isbn': '978-2-07-036050-2',
                'description': 'Conte philosophique satirique...',
                'date_publication': datetime(1759, 1, 1).date(),
                'categories': ['Philosophie', 'Littérature classique']
            },
            {
                'auteur': 'Isaac Asimov',
                'titre': 'Fondation',
                'isbn': '978-2-07-041800-7',
                'description': 'Premier tome de la saga Fondation...',
                'date_publication': datetime(1951, 1, 1).date(),
                'categories': ['Science-Fiction']
            },
            {
                'auteur': 'Agatha Christie',
                'titre': 'Le Crime de l\'Orient-Express',
                'isbn': '978-2-253-00482-3',
                'description': 'Célèbre roman policier mettant en scène Hercule Poirot...',
                'date_publication': datetime(1934, 1, 1).date(),
                'categories': ['Fiction']
            }
        ]

        def create_placeholder_image():
            """Create a simple placeholder image file"""
            # Create a simple 1x1 pixel image data (PNG format)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02D\x00\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            return ContentFile(png_data, name='placeholder.png')

        books = {}
        for book_data in books_data:
            cats = book_data.pop('categories')
            livre, created = Livre.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults=book_data
            )
            
            if created:
                # Add a placeholder image if none exists
                if not livre.image_couverture:
                    livre.image_couverture.save(
                        f'cover_{livre.isbn}.png',
                        create_placeholder_image(),
                        save=True
                    )
                
                # Add categories
                for cat_name in cats:
                    livre.categories.add(categories[cat_name])
                self.stdout.write(f'  Created book: {livre.titre}')
            
            books[livre.titre] = livre

        # 3. Create Exemplaires (Book Copies)
        self.stdout.write('Creating book copies...')
        exemplaires_data = [
            # Les Misérables (3 copies)
            ('Les Misérables', 'LM001', True, False, 'excellent', 'Édition reliée'),
            ('Les Misérables', 'LM002', True, False, 'bon', 'Édition poche'),
            ('Les Misérables', 'LM003', False, False, 'acceptable', 'Quelques annotations'),
            
            # Vingt mille lieues sous les mers (2 copies)
            ('Vingt mille lieues sous les mers', 'VM001', True, False, 'excellent', 'Édition illustrée'),
            ('Vingt mille lieues sous les mers', 'VM002', True, False, 'bon', 'Édition standard'),
            
            # L'Étranger (2 copies)
            ('L\'Étranger', 'ET001', True, False, 'excellent', 'Édition originale'),
            ('L\'Étranger', 'ET002', False, False, 'bon', 'Actuellement emprunté'),
            
            # Le Petit Prince (4 copies)
            ('Le Petit Prince', 'PP001', True, False, 'excellent', 'Édition illustrée'),
            ('Le Petit Prince', 'PP002', True, False, 'bon', 'Édition poche'),
            ('Le Petit Prince', 'PP003', True, False, 'acceptable', 'Usage fréquent'),
            ('Le Petit Prince', 'PP004', False, True, 'mauvais', 'Exemplaire perdu'),
            
            # Other books (1-2 copies each)
            ('Le Malade imaginaire', 'MI001', True, False, 'bon', 'Édition théâtrale'),
            ('Germinal', 'GE001', True, False, 'excellent', 'Édition annotée'),
            ('Germinal', 'GE002', True, False, 'bon', 'Édition poche'),
            ('Les Trois Mousquetaires', 'TM001', True, False, 'excellent', 'Édition intégrale'),
            ('Les Trois Mousquetaires', 'TM002', False, False, 'bon', 'Actuellement emprunté'),
            ('Candide', 'CA001', True, False, 'excellent', 'Édition critique'),
            ('Fondation', 'FO001', True, False, 'excellent', 'Première édition française'),
            ('Fondation', 'FO002', True, False, 'bon', 'Réédition récente'),
            ('Le Crime de l\'Orient-Express', 'CO001', True, False, 'bon', 'Édition poche'),
        ]

        exemplaires = []
        for titre, numero, disponible, perdu, etat, notes in exemplaires_data:
            livre = books[titre]
            exemplaire, created = Exemplaire.objects.get_or_create(
                livre=livre,
                numero_exemplaire=numero,
                defaults={
                    'disponible': disponible,
                    'perdu': perdu,
                    'etat': etat,
                    'notes': notes
                }
            )
            if created:
                exemplaires.append(exemplaire)
                self.stdout.write(f'  Created copy: {exemplaire}')

        # 4. Create sample users with proper passwords
        self.stdout.write('Creating sample users...')
        users = []
        users_data = [
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'first_name': 'Marie',
                'last_name': 'Dupont',
                'password': 'motdepasse123'  # 8+ characters
            },
            {
                'username': 'user2', 
                'email': 'user2@example.com',
                'first_name': 'Pierre',
                'last_name': 'Martin',
                'password': 'password123'  # 8+ characters
            },
            {
                'username': 'user3',
                'email': 'user3@example.com', 
                'first_name': 'Sophie',
                'last_name': 'Bernard',
                'password': 'testpass123'  # 8+ characters
            }
        ]
        
        for user_data in users_data:
            password = user_data.pop('password')
            user, created = Utilisateur.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'  Created user: {user.username}')
            users.append(user)

        # 5. Create sample borrows (only if we have exemplaires and users)
        if exemplaires and users:
            self.stdout.write('Creating sample borrows...')
            
            # Get some exemplaires for borrows
            ex1 = Exemplaire.objects.filter(numero_exemplaire='LM003').first()
            ex2 = Exemplaire.objects.filter(numero_exemplaire='ET002').first()
            ex3 = Exemplaire.objects.filter(numero_exemplaire='TM002').first()
            
            if ex1 and ex2 and ex3:
                # Active borrow
                emprunt1, created = Emprunter.objects.get_or_create(
                    exemplaire=ex1,
                    utilisateur=users[0],
                    defaults={
                        'date_demande': timezone.now() - timedelta(days=5),
                        'date_emprunt': timezone.now().date() - timedelta(days=3),
                        'date_retour_prevue': timezone.now().date() + timedelta(days=4),
                        'duree_jours': 7,
                        'accepter': True,
                        'statut': 'accepte',
                        'notes_admin': 'Emprunt approuvé pour étudiant'
                    }
                )
                if created:
                    self.stdout.write('  Created active borrow')
                
                # Overdue borrow
                emprunt2, created = Emprunter.objects.get_or_create(
                    exemplaire=ex3,
                    utilisateur=users[1],
                    defaults={
                        'date_demande': timezone.now() - timedelta(days=7),
                        'date_emprunt': timezone.now().date() - timedelta(days=5),
                        'date_retour_prevue': timezone.now().date() - timedelta(days=2),
                        'duree_jours': 3,
                        'accepter': True,
                        'statut': 'en_retard',
                        'notes_admin': 'Retard de 2 jours'
                    }
                )
                if created:
                    self.stdout.write('  Created overdue borrow')

        # 6. Create some sample reservations
        self.stdout.write('Creating sample reservations...')
        if users and books:
            # Get an unavailable book to reserve
            livre_reserve = books.get('L\'Étranger')
            if livre_reserve and users:
                reservation, created = Reservation.objects.get_or_create(
                    livre=livre_reserve,
                    utilisateur=users[2],
                    defaults={
                        'date_reservation': timezone.now().date(),
                        'statut': 'en_attente',
                        'notes': 'Réservation en attente de disponibilité'
                    }
                )
                if created:
                    self.stdout.write('  Created sample reservation')

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
        self.stdout.write(self.style.WARNING('Default passwords: motdepasse123, password123, testpass123'))
        self.stdout.write(self.style.WARNING('Note: Placeholder images were created for books'))