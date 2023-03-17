import spotipy
import time
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import threading

# --------------设置开始----------------------
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
# 必须与在Spotify开发者后台设置的Redirect URIs一致
redirect_uri = 'http://localhost:3000/callback'

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
OAuth_manager = SpotifyOAuth(
    client_id, client_secret, redirect_uri, scope='playlist-modify-public')
scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=OAuth_manager)
# 老帐号的用户名ID
old_username = 'YOUR_OLD_USERNAME'
# 新帐号的用户名ID
new_username = 'YOUR_NEW_USERNAME'
# 根据网速设置延时加入歌曲，网速慢就延时长一点，反之延时短一点
ADD_TO_PLAYLIST_DURATION = 0.2
# ----------------设置结束----------------------

# 获取老帐号的歌单
playlists = sp.user_playlists(old_username)

# 传入歌单的索引，将歌单中的歌曲加入到新帐号的歌单中
def transfer_playlist_process(index):
    try:
        playlist_id = playlists['items'][index]['id']
        # 获取一个歌单中的所有歌曲
        playlist = sp.playlist_tracks(playlist_id)
        print("playlist:\""+playlists['items']
              [index]['name']+"\" is transferring...")
        tracks = playlist['items']
        # tracks按加入时间排序
        tracks.sort(key=lambda x: x['added_at'])
        tracks_uri = [track['track']['uri'] for track in tracks if track['track']
                      is not None and track['track']['uri'].startswith('spotify:track')]
        # 在新账户下创建歌单
        new_playlist = sp.user_playlist_create(new_username, playlists['items'][index]['name'],
                                               playlists['items'][index]['public'], description=playlists['items'][index]['description'])

        for i in range(len(tracks_uri)):
            sp.playlist_add_items(new_playlist['id'], [tracks_uri[i]])
            # 根据网速设置延时加入歌曲，网速慢就延时长一点，反之延时短一点
            time.sleep(ADD_TO_PLAYLIST_DURATION)
    except Exception as e:
        print(e)


# 创建多个线程，每个线程负责一个歌单的转移
thread_list = []
for index in range(len(playlists['items'])):
    t = threading.Thread(target=transfer_playlist_process, args=(index, ))
    thread_list.append(t)
    t.start()
for t in thread_list:
    t.join()

# 歌单转移完成
print("All playlists are transferred successfully!")
