from app import db

class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean)
  seeking_description = db.Column(db.String())
  shows = db.relationship('Show', backref='artist', lazy=True)

  def __repr__(self):
    artist = f'<Artist id: {self.id}, name: {self.name}, city: {self.city}, ' \
      + f'state: {self.state}, phone: {self.phone}, genres: {self.genres}, ' \
      + f'image_link: {self.image_link}, facebook_link: {self.facebook_link},' \
      + f'website: {self.website}, genres: {self.genres}, ' \
      + f'seeking_venue: {self.seeking_venue}, seeking_description: {self.seeking_description}, ' \
      + f'shows: {self.shows}>\n'
    return artist