if exists('g:spotify')
    finish
endif
let g:spotify = 1

let s:script_name = '/script.py'
let s:plugindir = expand('<sfile>:p:h:h')

" escape strings for playlist/song names with quotes
function s:escape_string(str)
    let out = substitute(a:str, '"', '\\\\"', 'g')
    let out = substitute(l:out, "'", "\\\\'", 'g')
    return out
endfunction

function s:get_preview_command(fname)
    let preview_py = s:plugindir . '/scripts/playlist_preview.py'
    return 'python3 ' . l:preview_py . ' ' . a:fname . ' {}'
endfunction

function! s:getpos()
  return {'tab': tabpagenr(), 'win': winnr(), 'winid': win_getid(), 'cnt': winnr('$'), 'tcnt': tabpagenr('$')}
endfunction

" Configures and creates a popup window
function! s:configure_and_create_popup(width, height) abort
  let xoffset = 0.5
  let yoffset = 0.5

  " Use current window size for positioning relatively positioned popups
  let columns = &columns
  let lines = &lines - has('nvim')

  " Size and position
  let width = min([max([8, float2nr(columns * a:width)]), columns])
  let height = min([max([4, float2nr(lines * a:height)]), lines])
  let row = float2nr(yoffset * (lines - height))
  let col = float2nr(xoffset * (columns - width))

  " Managing the differences
  let row = min([max([0, row]), &lines - has('nvim') - l:height])
  let col = min([max([0, col]), &columns - l:width])

  call s:create_popup({
    \ 'row': row, 'col': col, 'width': width, 'height': height
  \ })
endfunction

" final function to create the selector popup
function! s:create_popup(opts) abort
  let buf = nvim_create_buf(v:false, v:true)
  let opts = extend({'relative': 'editor', 'style': 'minimal'}, a:opts)
  let win = nvim_open_win(buf, v:true, opts)
  silent! call setwinvar(win, '&winhighlight', 'Pmenu:,Normal:Normal')
  call setwinvar(win, '&colorcolumn', '')
endfunction

function! s:execute_cmd_in_term(ctx, command) abort
  let winrest = winrestcmd()
  let pbuf = bufnr('')
  let ppos = s:getpos()
  call s:configure_and_create_popup(0.9, 0.6)

  let fzf = { 'buf': bufnr(''), 'pbuf': pbuf, 'ppos': ppos,
            \ 'winrest': winrest, 'lines': &lines,
            \ 'columns': &columns, 'command': a:command , 'ctx': a:ctx}
  function! fzf.on_exit(id, code, ...)
    if bufexists(self.buf)
      execute 'bd!' self.buf
    endif
    call self.ctx['callback'](self.ctx)
  endfunction

  try
    let command = a:command
    call termopen(command, fzf)
    tnoremap <buffer> <c-z> <nop>
  endtry
  setlocal nospell bufhidden=wipe nobuflisted nonumber
  setf spotify
  startinsert
endfunction

" Produces the run command from an array of arguments
function s:get_run_command(arr) abort
    let l:script = s:plugindir . s:script_name
    let l:cmd =  l:script . ' ' . join(a:arr, ' ')
    return 'python3 '.cmd
endfunction

function! vimbeats#Run(...) abort
    let command = s:get_run_command(a:000)
    let out = system(l:command)
    return l:out
endfunction

function! vimbeats#CurrentlyPlaying() abort
    let l:out = vimbeats#Run('current-song')
    return out
endfunction

function! vimbeats#EnableShuffle() abort
    let l:out = vimbeats#Run('enable-shuffle')
    return out
endfunction

let s:play_toggle = 1
function! vimbeats#ToggleSpotify(...)
    if s:play_toggle
        echo 'Pausing spotify'
        call vimbeats#Run('pause')
        let s:play_toggle = 0
    else
        if exists('g:SpotifyDeviceID')
            call vimbeats#Run('play', '-d', g:SpotifyDeviceID)
        elseif a:0 == 1:
            let device_id = a:1
            call vimbeats#Run('play', '-d', l:device_id)
        else
            call vimbeats#Run('play')
        endif
        echo vimbeats#CurrentlyPlaying()
        let s:play_toggle = 1
    endif
endfunction

function! vimbeats#Next()
    silent call vimbeats#Run('next')
    echo vimbeats#CurrentlyPlaying()
endfunction

function! vimbeats#Prev()
    silent call vimbeats#Run('prev')
    echo vimbeats#CurrentlyPlaying()
endfunction

function! vimbeats#PlayContext(context_id)
    if exists('g:SpotifyDeviceID')
        call vimbeats#Run('play', '-d', g:SpotifyDeviceID, '-c', a:context_id)
    else
        call vimbeats#Run('play', '-c', a:context_id)
    endif

    " Attempt to print playlist name if context is a playlist
    let l:PLAYLIST_PREFIX = 'spotify:playlist:'
    if a:context_id[0:len(l:PLAYLIST_PREFIX)-1] ==# l:PLAYLIST_PREFIX
        let id = a:context_id[len(l:PLAYLIST_PREFIX):]
        echom "Playing " . vimbeats#Run('get-playlist', '-c', a:context_id)
    endif
endfunction

function! vimbeats#Queue(track_id)
    call vimbeats#Run('queue-song -c ' . a:track_id)
endfunction

function! vimbeats#SearchAndQueueTrack(query)
    let query_results = tempname()
    let results_file = tempname()

    let playlist_command = s:get_run_command([
                \'search',
                \'--query',
                \"'" . s:escape_string(a:query) . "'"]) . ' > ' . l:query_results
    call system(l:playlist_command)

    let command = 'cat ' . l:query_results
    let command .= " | python3 " . s:plugindir . '/scripts/track_names.py '
    let command .= ' | fzf --border --prompt ' . "'Search>'"
    let command .= ' --header "CTRL-r to Query Again"'
    let command .= " --bind 'ctrl-r:reload("
    let command .= s:plugindir . "/scripts/reload_query.sh {q} " . l:query_results
    let command .= ")'"
    let command .= " > " . l:results_file

    let ctx = {'results_file': l:results_file, 'song_file': l:query_results}
    let ctx['callback'] = function("s:queue_song_callback")

    call s:execute_cmd_in_term(l:ctx, l:command)
endfunction

" Select and play a playlist among current playlists
function! vimbeats#SelectAndPlayPlaylist()
    let playlist_file = tempname()
    let results_file = tempname()

    let playlist_command = s:get_run_command(['get-playlists']) . ' > ' . playlist_file
    call system(l:playlist_command)

    let command = 'cat ' . playlist_file . ' '
    let command .= "| python3 " . s:plugindir . '/scripts/playlist_names.py '
    let command .= '| fzf --border --prompt ' . "'Playlists>'"
    let command .= ' --preview="' . s:get_preview_command(l:playlist_file) . '" '
    let command .= " > " . results_file

    let ctx = {'results_file': results_file, 'playlist_file': playlist_file}
    let ctx['callback'] = function("s:play_playlist_callback")
    call s:execute_cmd_in_term(l:ctx, l:command)
endfunction

" Callback for playing a selected track
" ctx is a dictionary with two fields
"  * "song_file"  - the path of the file for all songs
"  * "results_file" - the path of the file for the chosen selection
function! s:queue_song_callback(ctx)
    let song_file = a:ctx['song_file']
    let results_file = a:ctx['results_file']
    if getfsize(l:results_file) == 0
        return
    endif

    let song_display_name = readfile(l:results_file)[0]

    let command = "jq -r $'.[] | select(.display_name==\"" . s:escape_string(song_display_name) . "\") | .id'"
    let command .= " < " . l:song_file

    " There's a chance a song can be duplicated in queries, so we index into
    " the first options
    let song_uri = trim(split(system(command))[0])
    let track_id = 'spotify:track:' . l:song_uri

    call vimbeats#Run('queue-song -c ' . l:track_id)

    " Get display name to dispayl
    echom "Queued: " . l:song_display_name
endfunction

" Callback for playing a selected playlist
" ctx is a dictionary with two fields
"  * "playlist_file"  - the path of the file for all playlists
"  * "results_file" - the path of the file for the chosen selection
function! s:play_playlist_callback(ctx)
    let playlist_file = a:ctx['playlist_file']
    let results_file = a:ctx['results_file']
    if getfsize(l:results_file) == 0
        return
    endif

    let playlist_name = readfile(l:results_file)[0]

    let command = "jq -r $'.[] | select(.name==\"" . s:escape_string(playlist_name) . "\") | .id'"
    let command .= " < " . playlist_file

    let playlist_id = trim(system(command))
    let id = 'spotify:playlist:' . playlist_id

    call vimbeats#PlayContext(id)
endfunction

function! vimbeats#SelectAndPlayFeaturedPlaylist()
    let playlist_file = tempname()
    let results_file = tempname()

    let playlist_command = s:get_run_command(['get-featured-playlists']) . ' > ' . playlist_file
    call system(l:playlist_command)

    let command = 'cat ' . playlist_file . ' '
    let command .= "| python3 " . s:plugindir . '/scripts/playlist_names.py '
    let command .= '| fzf --border --prompt ' . "'Featured>'"
    let command .= ' --preview="' . s:get_preview_command(l:playlist_file) . '" '
    let command .= " > " . results_file

    let ctx = {'results_file': results_file, 'playlist_file': playlist_file}
    let ctx['callback'] = function("s:play_playlist_callback")
    call s:execute_cmd_in_term(l:ctx, l:command)
endfunction

function! vimbeats#AddCurrentSongToLiked()
    let playlist_file = tempname()
    let playlist_cmd = s:get_run_command(['current-song', '--json']) . ' > ' . playlist_file
    call system(l:playlist_cmd)

    let id_command = 'jq -r .id' . ' < ' . l:playlist_file
    let id = trim(system(l:id_command))
    let display_name_command = 'jq -r .display_name' . ' < ' . l:playlist_file
    let display_name = trim(system(l:display_name_command))

    call vimbeats#Run('add-tracks', '--tracks', l:id)
    if v:shell_error == 0
        echom("Added current song to liked: " . display_name)
    else
        echom("An error occurred")
    endif
endfunction
