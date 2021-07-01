#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models.show import Show
from models.venue import Venue
from models.artist import Artist

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  locations = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  for location in locations:
    venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.state == location.state).filter(Venue.city == location.city).with_entities(Venue.id, Venue.name)
    data.append({"city": location.city,
      "state": location.state,
      "venues": venues})
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%'+ search_term + '%')).all()
  data = []
  for venue in venues:
    v = {
      "id": venue.id,
      "name": venue.name
    }
    data.append(v)
  response = {
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id).one()
  shows = Show.query.filter(Show.venue_id == venue_id).all()
  upcoming_shows = []
  past_shows = []
  for show in shows:
    artists = Artist.query.filter(Artist.id == show.artist_id).with_entities(Artist.id, Artist.name, Artist.image_link).all()
    for artist in artists:
      show_details = {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.isoformat(timespec='milliseconds') + "Z"
      }
      if show.start_time >= datetime.now():
        upcoming_shows.append(show_details)
      else:
        past_shows.append(show_details)
  data = venue.__dict__
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(past_shows)
  data["upcoming_shows_count"] = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    data = request.form
    venue = Venue(
      name = data['name'], 
      city = data['city'], 
      state = data['state'],
      address = data['address'], 
      phone = data.get('phone'), 
      genres = data.getlist('genres'),
      facebook_link = data.get('facebook_link'),
      image_link = data.get('image_link'),
      website = data.get('website_link'),
      seeking_talent = True if data.get('seeking_talent') == 'y' else False,
      seeking_description = data.get('seeking_description')
    )
    db.session.add(venue)
    db.session.commit()
    venue = Venue.query.filter(Venue.name == data['name']).one()
    flash('Venue ' + venue.name + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
    
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website
  form.seeking_talent.data = 'y' if venue.seeking_talent else ''
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    data = request.form
    venue = Venue.query.get(venue_id)
    venue.name = data['name']
    venue.city = data['city']
    venue.state = data['state']
    venue.address = data['address']
    venue.phone = data.get('phone')
    venue.genres = data.getlist('genres')
    venue.facebook_link = data.get('facebook_link')
    venue.image_link = data.get('image_link')
    venue.website = data.get('website_link')
    venue.seeking_talent = True if data.get('seeking_talent') == 'y' else False
    venue.seeking_description = data.get('seeking_description')
    db.session.commit()
    venue = Venue.query.get(venue_id)
    flash('Venue ' + venue.name + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({ 'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%'+ search_term + '%')).all()
  data = []
  for artist in artists:
    a = {
      "id": artist.id,
      "name": artist.name
    }
    data.append(a)
  response = {
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).one()
  upcoming_shows = []
  past_shows = []
  for show in artist.shows:
    venue = Venue.query.filter_by(id=show.venue_id).with_entities(Venue.id, Venue.name, Venue.image_link).one()
    show_details = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.isoformat(timespec='milliseconds') + "Z"
    }
    if show.start_time >= datetime.now():
      upcoming_shows.append(show_details)
    else:
      past_shows.append(show_details)
  data = artist.__dict__
  data["upcoming_shows"] = upcoming_shows
  data["past_shows"] = past_shows
  data["upcoming_shows_count"] = len(upcoming_shows)
  data["past_shows_count"] = len(past_shows)
  return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    data = request.form
    artist = Artist(
      name = data['name'], 
      city = data['city'], 
      state = data['state'],
      phone = data.get('phone', ''), 
      genres = data.getlist('genres'),
      facebook_link = data.get('facebook_link', ''),
      image_link = data.get('image_link', ''),
      website = data.get('website_link', ''),
      seeking_venue = True if data.get('seeking_venue') == 'y' else False,
      seeking_description = data.get('seeking_description', '')
    )
    db.session.add(artist)
    db.session.commit()
    artist = Artist.query.filter(Artist.name == data['name']).one()
    flash('Artist ' + artist.name + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
    
  return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website
  form.seeking_venue.data = 'y' if artist.seeking_venue else ''
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    data = request.form
    artist = Artist.query.get(artist_id)
    artist.name = data['name']
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data.get('phone', '')
    artist.genres = data.getlist('genres')
    artist.facebook_link = data.get('facebook_link', '')
    artist.image_link = data.get('image_link', '')
    artist.website = data.get('website_link', '')
    artist.seeking_venue = True if data.get('seeking_venue') == 'y' else False
    artist.seeking_description = data.get('seeking_description', '')
    db.session.commit()
    artist = Artist.query.get(artist_id)
    flash('Artist ' + artist.name + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    venue = Venue.query.filter_by(id = show.venue_id).with_entities(Venue.name).one()
    artist = Artist.query.filter_by(id = show.artist_id).with_entities(Artist.name, Artist.image_link).one()
    show_details = show.__dict__
    show_details["venue_name"] = venue.name
    show_details["artist_name"] = artist.name
    show_details["artist_image_link"] = artist.image_link
    show_details["start_time"] = show.start_time.isoformat(timespec='milliseconds') + "Z"
    data.append(show_details)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    data = request.form
    show = Show(
      artist_id = data['artist_id'],
      venue_id = data['venue_id'],
      start_time = data['start_time']
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
