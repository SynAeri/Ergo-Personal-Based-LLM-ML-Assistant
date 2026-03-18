" Ergo Neovim Plugin Entry Point

if exists('g:loaded_ergo')
  finish
endif
let g:loaded_ergo = 1

" Auto-setup on VimEnter
augroup ErgoSetup
  autocmd!
  autocmd VimEnter * lua require('ergo').setup()
augroup END
