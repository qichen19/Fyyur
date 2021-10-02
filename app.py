#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

migrate = Migrate(app,db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description=db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
   

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "Show"

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime())
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  artist = db.relationship(Artist, backref=db.backref('Show', cascade='all, delete'))
  venue = db.relationship(Venue, backref=db.backref('Show', cascade='all, delete'))

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by('city').all()
  data = []

  for city in cities:
    venues = db.session.query(Venue.id, Venue.name).filter_by(state=city.state).filter_by(city=city.city).order_by('name').all()
    venue_data = []
    data.append({
      'city': city.city,
      'state': city.state,
      'venues': venue_data
    })
    for venue in venues:
      upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).order_by('id').all()
      venue_data.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(upcoming_shows)
      })
     
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  data = []
  venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  for venue in venues:
    upcoming_shows = Show.query.filter_by(venue_id = venue.id).all()
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(upcoming_shows)
    })

  response={
    "count": len(venues),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  data = []
  shows = db.session.query(Show).join(Venue, Venue.id == Show.venue_id).filter(Venue.id == venue_id).all()
  past_shows = []
  upcoming_shows = []
  for show in shows:
    temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)

  data = {
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'address':venue.address,
        'phone': venue.phone,
        'genres':venue.genres,
        'website': venue.website,
        'facebook_link':venue.facebook_link,
        'image_link': venue.image_link,
        'seeking_talent':venue.seeking_talent,
        'seeking_description':venue.seeking_description,
        'upcoming_shows':upcoming_shows,
        'past_shows':past_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
  }

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  try:
      new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        address=form.address.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website=form.website.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
        genres=form.genres.data)
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      
  except ValueError as e:
      db.session.rollback()
      flash('An error occurred' + 'Venue ' + request.form['name'] + ' could not be listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  data = []
  artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  for artist in artists:
    upcoming_shows = Show.query.filter_by(artist_id = artist.id).all()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(upcoming_shows)
    })

  response={
    "count": len(artists),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  data = []
  shows = db.session.query(Show).join(Artist, Artist.id == Show.artist_id).filter(Artist.id == artist_id).all()
  past_shows = []
  upcoming_shows = []
  for show in shows:
    temp_show = {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)

  data = {
        'id': artist.id,
        'name': artist.name,
        'phone': artist.phone,
        'genres':artist.genres,
        'city': artist.city,
        'state': artist.state,
        'website': artist.website,
        'facebook_link':artist.facebook_link,
        'image_link': artist.image_link,
        'seeking_venue':artist.seeking_venue,
        'seeking_description':artist.seeking_description,
        'upcoming_shows':upcoming_shows,
        'past_shows':past_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
  }

  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

  # TODO: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website = form.website.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully edited!')
    except ValueError:
        db.session.rollback()
        flash('Error! Artist ' + artist.name + ' could not be updated.')
  else:
        flash('Errors in form validation')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website = form.website.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully edited!')
    except ValueError:
        db.session.rollback()
        flash('Error! Venue ' + venue.name + ' could not be updated.')
  else:
        flash('Errors in form validation')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website=form.website.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
        genres=form.genres.data)
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      
  except ValueError as e:
      db.session.rollback()
      flash('An error occurred' + 'Artist ' + request.form['name'] + ' could not be listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead flash('Artist ' + request.form['name'] + ' was successfully listed!').
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.order_by(Show.start_time.desc()).all()
  data = []
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
    artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
    data.append({
      "venue_id": show.venue_id,
      "artist_id": show.artist_id,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M"),
      "venue_name": venue.name,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link
    })
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  date_format = '%Y-%m-%d %H:%M:%S'
  try:
      new_show = Show(
        start_time=datetime.strptime(str(form.start_time.data), date_format),
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data
      )

      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
      
  except ValueError as e:
      db.session.rollback()
      flash('An error occurred' + 'Show could not be listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
