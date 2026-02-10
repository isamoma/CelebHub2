#!/usr/bin/env python
"""Add test celebrities to the database for manual testing."""

import os
import sys
from app import create_app
from app.models import Celebrity, User, USE_MONGO

app = create_app()

with app.app_context():
    # Create test admin user
    test_user = User(username='admin')
    test_user.set_password('admin')
    
    if USE_MONGO:
        test_user.save()
    else:
        from app import DB
        DB.session.add(test_user)
        DB.session.commit()
    
    print("✓ Admin user created (admin/admin)")
    
    # Create test celebrities with social media links
    celebs_data = [
        {
            'name': 'Sauti Sol',
            'bio': 'World-renowned Kenyan music group',
            'youtube': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'tiktok': 'https://vm.tiktok.com/ZMe4K2ABC',
            'spotify': 'https://open.spotify.com/artist/03D4yvfR7LdJlnZvzb3jdp',
            'featured': True
        },
        {
            'name': 'Nairobi Opera',
            'bio': 'Contemporary East African opera ensemble',
            'youtube': 'https://youtu.be/jNgP6d9HraI',
            'tiktok': None,
            'spotify': 'https://open.spotify.com/artist/5lQvWLjc8khvQNDlOB7FQw',
            'featured': True
        },
        {
            'name': 'Ethic Entertainment',
            'bio': 'Popular East African hip-hop group',
            'youtube': 'https://www.youtube.com/embed/7OPYzXYxCl0',
            'tiktok': 'https://vm.tiktok.com/ZMeS2gCXd',
            'spotify': 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMwbk',
            'featured': False
        }
    ]
    
    for celeb_data in celebs_data:
        # Check if already exists
        name = celeb_data['name']
        if USE_MONGO:
            existing = Celebrity.objects(name=name).first()
        else:
            from app import DB
            existing = Celebrity.query.filter_by(name=name).first()
        
        if not existing:
            from app.utils import extract_youtube_id, extract_tiktok_id, extract_spotify_id
            # Normalize URLs using extraction functions
            yt = extract_youtube_id(celeb_data['youtube']) if celeb_data['youtube'] else None
            tk = extract_tiktok_id(celeb_data['tiktok']) if celeb_data['tiktok'] else None
            sp = extract_spotify_id(celeb_data['spotify']) if celeb_data['spotify'] else None
            
            celeb = Celebrity(
                name=celeb_data['name'],
                slug=celeb_data['name'].lower().replace(' ', '-'),
                bio=celeb_data['bio'],
                youtube=yt or celeb_data['youtube'],
                tiktok=tk or celeb_data['tiktok'],
                spotify=sp or celeb_data['spotify'],
                featured=celeb_data['featured']
            )
            if USE_MONGO:
                celeb.save()
            else:
                from app import DB
                DB.session.add(celeb)
                DB.session.commit()
            print(f"✓ Added celebrity: {name}")
        else:
            print(f"⊘ {name} already exists")
    
    print("\n✅ Test data setup complete!")
    print("\nYou can now:")
    print("1. Visit http://127.0.0.1:5000 to see featured celebrities")
    print("2. Log in with admin/admin at http://127.0.0.1:5000/admin/login")
    print("3. Click profile links to test YouTube/TikTok/Spotify embeds")
