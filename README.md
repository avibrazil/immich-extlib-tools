# Immich simple API for Python and tools to work with external libraries

`pip install immich_exlib_tools --user`

So you have spent the last years carefully organizing your photos in a nice
folder structure, like me:

```
📂Party and People/
    📂2021-08-20 A day in Salem/
    📂2021-09-02／10-14 Max and his skate/
    📂2023-99 Camera Roll/
    📂2024-99 Camera Roll/
    📂2025-02-23／03-04 Carnaval 2025/

📂Trips National/
    📂2021-99 Guarujá/
    📂2023-02-21／28 Carnaval in Rio, Paraty, São Paulo with Mary ＆ John/
    📂2023-10-12／15 PETAR — Parque Estadual Turístico do Alto Ribeira/

📂Trips International/
    📂2004-08 Germany, Ludwigsburg, Munich, Salzburg/
    📂2021-07-23／25 Weekend in New York City/
    📂2025-01 Slovenia, Veneza, Zurich/
    📂2007-09-14／10-09 🇺🇿Uzbekistan, 🇰🇬Kyrgyzstan, 🇨🇳Kashgar, 🇷🇺Moscow, 🇫🇷Paris
```

Then you add these root folders to Immich through its
[External Library](https://docs.immich.app/features/libraries) feature only to
learn that all your amazing folders/albums structure is ignored.

I created a set of commands that will recreate on Immich your albums based on
your folder structure.

And for that I created also a simple, effective and generic Python module that
you can use to simplify talking to Immich REST API.

## The Tools/Commands

There are 2 tools: `immich_albums_from_folders` and `immich_dlna_photoframe`

You need to `pip install pandas --user` to use these tools. And also
`dnf install ImageMagick-heic` for the HEIC conversion feature of
`immich_dlna_photoframe`.

Since I run this commands a lot, and they get a lot of long and complicated
parameters, I encapsulated it all in systemd service files in my Linux user
account (not root), installed in `$HOME/.config/systemd/user/`,

### immich_albums_from_folders

- Synchronizes filesystem folders structure with Immich albums, converting
  folder names into something nicer for Immich.
- Mark photos as favorites in Immich if their file names have some special
  chars (I use ★ or ♥︎).

So everytime I add or remove folders and photos to my collection in the
filesystems, I make Immich rescan it and then I run `immich_albums_from_folders`
like this:

```shell
immich_albums_from_folders \
    --immich-url       'https://photos.mycloud.net:444/api' \
    --immich-api-key   'aaa...zzz' \
    --favorite-pattern '★|♥︎' \
    --from-to          '(?P<dummy>.*)/(?P<year>\d{4})-99[\s\-](?P<name>Camera Roll)' 'Generic/\g<name> (\g<year>)' \
    --from-to          '/(?P<year>\d{4})-99[\s\-](?P<name>.*)'            '/\g<name> (\g<year>)' \
    --from-to          '/(?P<date>[\d\-\s／]*)[\s\-](?P<name>.*)'         '/\g<name> (\g<date>)' \
    --from-to          'Trips National/'                                  '🚗 ' \
    --from-to          'Trips International/'                             '✈️ ' \
    --from-to          'Party and People/'                                '🥳 ' \
    --from-to          'Generic/'                                         '📸 ' \
    --from-to          '_'                                                ' '
```

Or I just run `systemctl start --user immich-albums`.

This sequence of regular expressions will use my folder names to create the following Immich albums:

| Immich album name | Original filesystem folder structure |
--------------------|--------------------------------------|
| 🥳 A day in Salem (2021-08-20) | 📂Party and People/2021-08-20 A day in Salem
| 🥳 Max and his skate (2021-09-02／10-14) | 📂Party and People/2021-09-02／10-14 Max and his skate
| 📸 Camera Roll (2023) | 📂Party and People/2023-99 Camera Roll
| 📸 Camera Roll (2024)| 📂Party and People/2024-99 Camera Roll
| 🥳 Carnaval 2025 (2025-02-23／03-04) | 📂Party and People/2025-02-23／03-04 Carnaval 2025
| 📸 Guarujá (2021)   | 📂Trips National/2021-99 Guarujá
| 🚗 Carnaval in Rio, Paraty, São Paulo with Mary ＆ John (2023-02-21／28)  | 📂Trips National/2023-02-21／28 Carnaval in Rio, Paraty, São Paulo with Mary ＆ John
| 🚗 PETAR — Parque Estadual Turístico do Alto Ribeira (2023-10-12／15)   | 📂Trips National/2023-10-12／15 PETAR — Parque Estadual Turístico do Alto Ribeira
| ✈️ Germany, Ludwigsburg, Munich, Salzburg (2004-08) | 📂Trips International/2004-08 Germany, Ludwigsburg, Munich, Salzburg
| ✈️ Weekend in New York City (2021-07-23／25)  | 📂Trips International/2021-07-23／25 Weekend in New York City
| ✈️ Slovenia, Veneza, Zurich (2025-01)  | 📂Trips International/2025-01 Slovenia, Veneza, Zurich
| ✈️ 🇺🇿Uzbekistan, 🇰🇬Kyrgyzstan, 🇨🇳Kashgar, 🇷🇺Moscow, 🇫🇷Paris (2007-09-14／10-09) | 📂Trips International/2007-09-14／10-09 🇺🇿Uzbekistan, 🇰🇬Kyrgyzstan, 🇨🇳Kashgar, 🇷🇺Moscow, 🇫🇷Paris

Also, favorite semantics is taken from file names. Here is how I name my photo files:
```
2021.07.24-17.43.15 • Manhattan skyline from sailboat cruise 【Avi Alkalay·︎iPhone 12 Pro】.heic
2007.09.14-15.16.15 ♥ Sena River 【Avi Alkalay·Sony DSC-W30】.jpg
2021.07.23-22.23.44 ★ Family waiting for dinner in a New York restaurant 【Avi Alkalay·iPhone 12 Pro】.heic
```

So 2 last examples will be marked as favorites in Immich because their file
names matched `--favorite-pattern '★|♥︎'`.

Notice how I extensively use emoji and Unicode chars in both folder names and
file names. There is no reason for your photos in the filesystem to have boring
names that don't say nothing as IMG5678.JPG. Most of the sematics of your photo
collection must reside in the simplest tool, which is the filesystem. Immich
just adds usability and remote access to your archives.

### immich_dlna_photoframe

I tried many apps to display photos in my living room LG webOS TV, but they all
failed. Either there is no native Immich app ready to install, web apps are bad,
or the TV doesn't support more advanced formats (that I use a lot), such as
HEIC.

So the best solution that I found is to run **[ReadyMedia (formerly known
as MiniDLNA)](https://sourceforge.net/projects/minidlna/)** daemon in my home
server, serving a folder of photo files, then I use the **Media App** which is
already included in webOS, to access and play my photos as a giant photoframe.

The result is so smooth, simple and stuning that sometimes I need to turn off
the TV off because we can't stop watching.

Of course that I don't play any photo, but a curated selection of more than 1000
photos from all my collection. This curation is an Immich album that I call **★♥︎Top**.

So the `immich_dlna_photoframe` command will retrieve this album and:

- Convert HEIC to JPEG in the target folder (the folder served by DLNA)
- Link JPEG original files to the target folder
- Add a prefix to all file names so they get randomized, because LG's Media App
  plays them as they are listed and DLNA serves them arphabetically ordered, which is boring

So I run it like this:

```
immich_dlna_photoframe \
    --immich-url       'https://photos.mycloud.net:444/api' \
    --immich-api-key   'aaa...zzz' \
    --album            '★♥︎Top' \
    --target           '/media/Media/Photos/Photoframe' \
    --randomize
```

Or I just run `systemctl start --user photoframe`.

It takes about 5 minutes to convert the HEICs in my +1000 selection in `★♥︎Top`
Immich album. And I run it every day at midnight, so I get the selection
reordered every day in a random sequence.

## The Python API

```python
import immich

im=immich.Immich(
    url='https://photos.mycloud.net/api',
    apiKey='aaa...zzz',
    validCertOnly=True
)

# Do easier operations as documented in Immich REST API (https://api.immich.app/introduction)
im.get('/libraries')
im.put('/albums/assets', dict_with_parameters)
im.delete('/assets', dict(ids=[asset_id1,asset_id2,asset_id3]))
newAlbumId = im.post(
    "/albums",
    dict(
        # Create album with this name
        albumName = "★♥︎Top",
        assetIds  = list(...),
        description = "Some descriptive description"
    )
)['id']

# Additional 2 convenient methods
json_response_converted_to_dict = im.assets(dict(albumIds=[id1,id2], order='asc'))
all_albums = im.albums()

# Use with Pandas
import pandas

assets = pandas.DataFrame(im.assets(dict(albumIds=[id1,id2], order='asc')))
albums = pandas.DataFrame(im.albums())
)
```
