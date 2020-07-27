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
  - id: x_view
    type: u4
  - id: y_view
    type: u4
  - id: trash_1
    size: 40016
  - id: bmap_size
    type: bmap_size
  - id: bmap_tile
    type: bmap_tile
  - id: tmap
    type: tmap
  - id: trash_2
    size: 10000
  - id: bmap_id
    type: bmap_id
  - id: bmap_step
    type: bmap_step
  - id: step_current
    type: u4
  - id: step_total
    type: u4
  - id: pause_step
    type: s4
    repeat: expr
    repeat-expr: _root.dir.uncompr_size[11]/4
  - id: tarr
    type: u4
    repeat: expr
    repeat-expr: _root.dir.uncompr_size[12]/4
  - id: pause
    type: u4
    
    
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
  bmap_size:
    seq:
      - id: uncompr_size
        type: u4
      - id: compr_size
        type: u4
      - id: crc32
        type: u4
      - id: data
        type: u1
        repeat: expr
        repeat-expr: compr_size
  bmap_tile:
    seq:
      - id: uncompr_size
        type: u4
      - id: compr_size
        type: u4
      - id: crc32
        type: u4
      - id: data
        type: u1
        repeat: expr
        repeat-expr: compr_size      
  tmap:
    seq:
      - id: uncompr_size
        type: u4
      - id: compr_size
        type: u4
      - id: crc32
        type: u4
      - id: data
        type: u1
        repeat: expr
        repeat-expr: compr_size     
  bmap_id:
    seq:
      - id: uncompr_size
        type: u4
      - id: compr_size
        type: u4
      - id: crc32
        type: u4
      - id: data
        type: u2
        repeat: expr
        repeat-expr: compr_size/2      
  bmap_step:
    seq:
      - id: uncompr_size
        type: u4
      - id: compr_size
        type: u4
      - id: crc32
        type: u4
      - id: data
        type: u4
        repeat: expr
        repeat-expr: compr_size/4