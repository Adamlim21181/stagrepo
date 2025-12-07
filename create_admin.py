"""
Admin user creation script for StagGymnastics platform.
Run this script to create an admin user with full privileges.
"""

from create_app import create_app
from extensions import db
import models
from werkzeug.security import generate_password_hash

def create_roles():
    """Create the basic roles if they don't exist."""
    app = create_app()
    with app.app_context():
        # Create Admin role
        admin_role = models.Roles.query.filter_by(id=1).first()
        if not admin_role:
            admin_role = models.Roles(id=1, name='Admin')
            db.session.add(admin_role)
            print("Created Admin role")
        
        # Create Judge role
        judge_role = models.Roles.query.filter_by(id=2).first()
        if not judge_role:
            judge_role = models.Roles(id=2, name='Judge')
            db.session.add(judge_role)
            print("Created Judge role")
        
        # Create User role
        user_role = models.Roles.query.filter_by(id=3).first()
        if not user_role:
            user_role = models.Roles(id=3, name='User')
            db.session.add(user_role)
            print("Created User role")
        
        db.session.commit()
        print("Roles setup complete")

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        existing_admin = models.Users.query.filter_by(email='adamlimnz@gmail.com').first()
        if existing_admin:
            print("Admin user already exists!")
            print(f"Username: {existing_admin.username}")
            print(f"Email: {existing_admin.email}")
            return existing_admin
        
        # Create admin user
        admin_user = models.Users(
            username='adamlimnz',
            email='adamlimnz@gmail.com',
            first_name='Adam',
            last_name='Lim',
            password=generate_password_hash('StagScoring!'),
            role_id=1  # 1 = Admin role
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print("Username: adamlimnz")
        print("Email: adamlimnz@gmail.com")
        print("Password: StagScoring!")
        print("Role: Admin")
        return admin_user

def show_all_users():
    app = create_app()
    with app.app_context():
        print("\n=== ALL USERS ===")
        users = models.Users.query.all()
        if not users:
            print("No users found in database.")
            return
        
        for user in users:
            role = "Admin" if user.role_id == 1 else "Judge" if user.role_id == 2 else "User"
            print(f"- {user.username} ({user.email}) - Role: {role}")

if __name__ == "__main__":
    create_roles()  # Create roles first
    create_admin_user()
    show_all_users()