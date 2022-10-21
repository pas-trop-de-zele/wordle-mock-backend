# wordle-mock-backend

## Testing

```
pytest test_api.py
```

## How to launch app

```
$ foreman start
```

## Login using httpie

```
http POST <insert local url here>/login --auth <username>:<password>
```

## Register using httpie

```
http POST <insert local url here>/register username=<new username> password=<new password>
```

## Start a game using httpie

```
http  <insert local url here>/startgame username=<new username>
```

## list all the games using httpie

```
http  <insert local url here>/listAllGames/<string:username>
```

## retrive a games using httpie

```
http  <insert local url here>/retrievegame/<int:gameid>
```
