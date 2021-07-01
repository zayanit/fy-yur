from app import db

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  genres = db.Column(db.ARRAY(db.String))
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean)
  seeking_description = db.Column(db.String())
  shows = db.relationship('Show', backref='venue', lazy=True)

  def __repr__(self):
    venue = f'<Venue id: {self.id}, name: {self.name}, city: {self.city}, '  \
      + f'state: {self.state}, address: {self.address}, phone: {self.phone}, ' \
      + f'image_link: {self.image_link}, facebook_link: {self.facebook_link}, ' \
      + f'website: {self.website}, genres: {self.genres}, ' \
      + f'seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}, ' \
      + f'shows: {self.shows}>\n'
    return venue