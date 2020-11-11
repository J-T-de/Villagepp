meta:
  id: aiv
  title: AI Village
  application: 
    - Stronghold Crusader
    - Stronghold Crusader Extreme
    - Village
  file-extension: aiv
  endian: le
  
seq:
  - id: dir
    type: dir
  - id: sec
    repeat: expr
    repeat-expr: _root.dir.sec_cnt
    type:
      switch-on: _root.dir.is_compr[_index]
      cases:
        0: uncompr_sec(_index)
        1: compr_sec
    
types:
  dir:  # directory
    seq:
      - id: dir_size
        type: u4
      - id: file_size_without_dir
        type: u4
      - id: sec_cnt
        type: u4
      - id: magic
        contents: [0xc8, 0x00, 0x00, 0x00]
      - id: zeros1
        contents: [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
      - id: uncompr_size
        type: u4
        repeat: expr
        repeat-expr: 100
      - id: compr_size
        type: u4
        repeat: expr
        repeat-expr: 100
      - id: id
        type: u4
        repeat: expr
        repeat-expr: 100
      - id: is_compr
        type: u4
        repeat: expr
        repeat-expr: 100
      - id: offset
        type: u4
        repeat: expr
        repeat-expr: 100
      - id: zeros2
        contents: [0x00, 0x00, 0x00, 0x00]
  uncompr_sec:  # uncompressed Section
    params:
      - id: i
        type: u4
    seq:
      - id: data
        type: s4
        repeat: expr
        repeat-expr: _root.dir.uncompr_size[i]/4        
  compr_sec:    # compressed Section
    seq:
      - id: uncompr_size
        type: u4
      - id: compr_size
        type: u4
      - id: crc32
        type: u4
      - id: data
        size: compr_size