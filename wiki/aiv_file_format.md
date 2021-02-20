# AIV File Format

The aiv consists of a directory, which specifies where and how the data is stored, and the actual data. Thanks to [gynt](https://github.com/gynt) from the [sourcehold maps](https://github.com/sourcehold/sourcehold-maps) team, who found out how the directory works!

You can find the aiv file structure in the [Kaitai](http://kaitai.io/) format, one time the general layout in [`aiv.ksy`](https://github.com/J-T-de/Villagepp/blob/main/structure/aiv.ksy), and one time an 'unrolled' version [`aiv_explicit.ksy`](https://github.com/J-T-de/Villagepp/blob/main/structure/aiv_explicit.ksy) which includes the names specified later in this document. For historical reasons, there is also the aiv file structure in the [construct](https://github.com/J-T-de/Villagepp/blob/main/structure/aiv.py) format [`aiv.py`](https://github.com/J-T-de/Villagepp/blob/main/structure/aiv.py). The actual (de-) serialization is done [here](https://github.com/J-T-de/Villagepp/blob/main/aiv.py).

# Directory

The directory structure was copied from the map file format. It consists of a header with
- the directory size `size` (always 2036)
- the file size without directory `fswd`, so that `file_size = size + fswd` 
- the section counter `sec_cnt` (always `14`)
- the version (always `200`, indicating its an aiv and no map)

and 5 arrays specifying the properties of the following `14` sections

- the uncompressed size of each section `uncompr_size`
- the compressed size of each section `compr_size`
- an internal name `id`, ranging from `2001` to `2014`
- the information, whether or not the section is compressed, `is_compr`
- and the `offset`, where each section is stored (`total_offset = dir_size + offset`).

# Data Sections

The data sections contain the actual aiv data. Some of the data is used ingame and in the aiv editor and some of the data is exclusively used in the aiv editor. 

| Section   | Name              | Usage
| :-------: | :---------------- | :------
| 2001      | `x_view`          | editor
| 2002      | `y_view`          | editor
| 2003      | `random`          | editor
| 2004      | `bmap_size`       | editor
| 2005      | `bmap_tile`       | editor
| 2006      | `gmap`            | editor
| 2007      | `bmap_id`         | game + editor
| 2008      | `bmap_step`       | game + editor
| 2009      | `step_cur`        | editor
| 2010      | `step_tot`        | editor
| 2011      | `parr`            | game + editor
| 2012      | `tarr`            | game + editor
| 2013      | `tmap`            | editor
| 2014      | `pause`           | game + editor

In general, the data can be interpreted as
- a scalar
- an array
- a map/matrix

Before discussing each section, we want to state that the map sections are `100x100` arrays, enumerated from top to bottom (index `i`) and left to right (index `j`).

## x_view and y_view

Specifies the viewport within the aiv editor, `x_view` goes from left (0) to right (0x97F=2431), `y_view` from top (0) to bottom (0x97F=2431). As a single tile has `tile_size=32px`, and the resolution of the visible part of the aiv has `resolution=768px` in the original editor, we have `2431+1+resolution=100*tile_size`, so the viewport really relates to the in-editor coordinates.

## random

Internal state of the random number generator. Presumably only used to initialize the `gmap`. Shout-out to [JuGGerNaunT](https://www.moddb.com/members/juggernaunt) for this finding!

## bmap_size

Map, where each tile stores the size of the building which stands on it. This is used by the editor to center the names.

## bmap_tile

Map, where each tile stores which tile within the tileset `color tiles.bmp`/ `color tiles.gm1` is used within the editor. The top left corner is tile 1, which has a frame on the left and on the top, tile 5 has only a top frame and so on.

## gmap

Map, where each tile stores which grass tile of the tileset `color tiles.bmp`/ `color tiles.gm1` is used within the editor (0 to 7). Probably initialized using the random number generator with internal state `random`.

## bmap_id

Map, where each tile stores the id of the building which stands on it.

## bmap_step

Map, where each tile stores the step in which the building specified in bmap_id gets built on it.

## step_cur and step_tot

In the aiv editor, the current step `step_cur-1` and the total steps `step_tot-1` are displayed. In step 0, nothing is built, and in step 1, the keep as well as the border tiles are built.

## parr

Array of uint32_t, where each step in which a pause happens is written. For vanilla aiv, length is either 10 or 50, the zeroth element always `0` and padded to end with `-1`.

## tarr

An `24x10` array of uint32_t, where the position of each rally point is encoded. Each unit type has potentially 10 rally points. For example, crossbowmen have unit_id 7, so the first rally point is `tarr[7,0]` and the last one `tarr[7,9]`, and the `i`- and `j`-position of the first rally point of crossbowmen can be determined via

`j, i = divmod(tarr[7,0], 100) `

## tmap

Map, where the rally points specified in `tarr` are visualized for the editor. It is not completely clear why, because only the unit id is saved (and not which entry). This seems to relate to the bug, when one has two units on the same spot: if you delete the top one, the tmap entry is zero, not the id of the unit below.

## pause

Specifies the pause done in each step of parr.