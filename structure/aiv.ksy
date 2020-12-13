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
      - id: size    # always 2036
        type: u4
      - id: fswd    # file size without directory
        type: u4
      - id: sec_cnt # always 14
        type: u4
      - id: version # always 200
        type: u4
      - id: padding0
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
      - id: padding1
        contents: [0x00, 0x00, 0x00, 0x00]

  uncompr_sec:  # uncompressed section
    params:
      - id: i
        type: u4
    seq:
      - id: data
        size: _root.dir.uncompr_size[i]

  compr_sec:    # compressed section
    seq:
      - id: uncompr_size
        type: u4
      - id: compr_size
        type: u4
      - id: crc32
        type: u4
      - id: data
        size: compr_size