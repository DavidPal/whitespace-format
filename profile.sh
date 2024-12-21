python -m cProfile whitespace_format.py \
      --check-only --color --verbose \
			--new-line-marker linux \
			--normalize-new-line-markers \
			--add-new-line-marker-at-end-of-file \
			--remove-trailing-whitespace \
			--remove-trailing-empty-lines \
			--normalize-non-standard-whitespace replace \
			--normalize-whitespace-only-files empty \
			~/git-personal/linux/fs
