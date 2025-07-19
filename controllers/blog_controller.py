from db import db
from models.blog_model import BlogModel

class BlogController:
    
    def create_post(self, title, content, author_id, image_url=None):
        post = BlogModel(
            title=title,
            content=content,
            author_id=author_id,
            image_url=image_url
        )
        db.session.add(post)
        db.session.commit()
        return post
    def update_post(self, post_id, title=None, content=None, image_url=None):
        post = BlogModel.query.get(post_id)
        if not post:
            return None
        
        if title:
            post.title = title
        if content:
            post.content = content
        if image_url:
            post.image_url = image_url
        
        db.session.commit()
        return post
    def delete_post(self, post_id):
        post = BlogModel.query.get(post_id)
        if not post:
            return None
        
        db.session.delete(post)
        db.session.commit()
        return post
    def get_all_posts(self):
        return BlogModel.query.order_by(BlogModel.created_at.desc()).all()
    
    def get_recent_posts(self, limit=3):
        return BlogModel.query.order_by(BlogModel.created_at.desc()).limit(limit).all()
    
    def get_post_by_id(self, post_id):
        return BlogModel.query.get(post_id)
    
    def get_posts_by_author(self, author_id):
        return BlogModel.query.filter_by(author_id=author_id).all()
    
    def get_last_post_id(self):
        last_post = BlogModel.query.order_by(BlogModel.id.desc()).first()
        return last_post.id if last_post else None