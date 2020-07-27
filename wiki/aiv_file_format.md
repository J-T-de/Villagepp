# AIV File Format

The aiv consists of a directory, which specifies where and how the data is stored, and the actual data. Thanks to [gynt](https://github.com/gynt) from the [sourcehold maps](github.com/sourcehold/sourcehold-maps) team, who found out how the directory works!  
You can find the aiv file structure in the Kaitai format, one time the general layout in `aiv.ksy`, and one time an 'unrolled' version `aiv_explicit.ksy` which includes the names specified later in this document. For the actual deserialization and serialization we use the `aiv.py`, which includes more logic.

# Directory

The directory structure was copied from the map file format. It consists of a header with
- the directory size `dir_size`
- the `file_size_without_directory`, so `file_size = dir_size + file_size_without_directory` 
- the section counter `sec_cnt` (always `14`)
- the magic number `200` (indicating an aiv and no map)

and 5 arrays specifying the properties of the following `14` sections

- the uncompressed size of each section `uncompr_size`
- the compressed size of each section `compr_size`
- an internal name `id`, ranging from `2001` to `2014`
- the information, whether or not the section is compressed, `is_compr`
- and the `offset`, where each section is stored (`total_offset = dir_size + offset`).

# Data Sections

The data sections contain the actual aiv data. Some of the data is used ingame and in the aiv editor, some of the data is unsed exclusively in the aiv editor and some data does not make sense up to now. 

| Section   | Name              | Usage
| :-------: | :---------------- | :------
| 2001      | `x_view`          | editor
| 2002      | `y_view`          | editor
| 2003      | `trash_1`         | unknown
| 2004      | `bmap_size`       | editor
| 2005      | `bmap_tile`       | editor
| 2006      | `tmap`            | editor
| 2007      | `trash_2`         | unknown
| 2008      | `bmap_id`         | game + editor
| 2009      | `bmap_step`       | game + editor
| 2010      | `step_current`    | editor
| 2011      | `step_total`      | editor
| 2012      | `pause_step`      | game + editor
| 2013      | `tarr`            | game + editor
| 2014      | `pause`           | game + editor

In general, the data can be interpreted as
- a scalar
- an array
- a map/matrix

Before discussing the each of the section, we want to state that the map section are `100 x 100`, enumerated from left to right, from top to bottom.

## `x_view` and `y_view`

Specifies the viewport within the aiv editor, x_view goes from left (0) to right (0x97F=2431), y_view from top (0) to bottom (0x97F=2431).

## `trash_1`

Pseudo-random data. This gets initialized when starting the editor, and does not change when editing the aiv. It seems like it has a 16 byte header and then a uint32_t-map, where the most significant bit is always 0, and no entry with value 0. Filling this section with random data does not break the aiv.

## bmap_size

Map, where each tile stores the size of the building which stands on it. This is used by the editor to center the names.

## bmap_tile

Map, where each tile stores which tile within the tileset `color tiles.bmp`/ `color tiles.gm1` is used within the editor. The top left corner is tile one, which has a frame on the left and on the top, the tile 5 has only a top frame and so on.

## tmap

Map, where the rally points specified in tarr are visualized for the editor. It is not completely clear why, because only the unit id is saved (and not which entry). This seems to relate to the bug, when one has two units on the same spot: if you delete the top one, the tmap entry is zero, not the id of the unit below.

## trash_2

Pseudo-random data. This gets initialized when starting the editor, and does not change when editing the aiv. All entries are uint8_t from 0 to 7. Filling this section with random data does not break the aiv.

## bmap_id

Map, where each tile stores the id of the building which stands on it.

## bmap_step

Map, where each tile stores the step in which the building specified in bmap_id gets built on it.

## step_current and step_total

In the aiv editor, step_current-1 and step_total-1 is displayed. In step 0, everything is empty, in step 1, the border tiles as well as the keep is built.

## pause_step

Array of uint32_t, where each step in which a pause happens is written. For vanilla aiv, length is either 10 or 50, the zeroth element always 0x00 and padded to end with 0xFF.

## tarr

Array of uint32_t, where the position of each rally point is encoded. Each unit type has potentially 10 rally points. For example, crossbowmen have unit_id 7, so the first rally point is `tarr[70]` and the last one `tarr[79]`, and the `x`- and `y`-position of the first rally point of crossbowmen can be determined via

`x, y = divmod(tarr[70], 100) `

## pause

Specifiese the pause of pause_step.