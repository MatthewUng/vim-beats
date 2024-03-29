# Vim-Beats


Simple spotify integration with vim.

## Set-up
1. Create a spotify app [[link](https://developer.spotify.com/dashboard)]
2. Take note of the client_id and client_secret
3. Run `python3 auth_script.py` and follow the instructions. The script should prompt you for your 
client id, client secret, and ask to authorize spotify access 
4. Update your vimrc with your desired macros
e.g.
```
" ID of device to play.  Influences what device `PlayContext` plays on.
let g:SpotifyDeviceID = '<device id>'
nnoremap <silent> <leader>mm :call vimbeats#ToggleSpotify('<device_id>')<cr>
nnoremap <leader>mj :call vimbeats#Next()<cr>
nnoremap <leader>mk :call vimbeats#Prev()<cr>
nnoremap <leader>m1 :call vimbeats#PlayContext("spotify:playlist:7DUzBdvt1lrM0IVKG93Ibh")<cr>
command! -nargs=+ SearchAndQueue :call vimbeats#SearchAndQueue(<q-args>)
nnoremap <leader>mq :SearchAndQueue<space>
```


## Misc.
Q: How do I obtain a playlist ID?  
A: https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids

Q: How do I obtain a device ID?  
A: Have Spotify running on the target device and try `python3 ./script get-devices`.
You can find the device id from the printed output
