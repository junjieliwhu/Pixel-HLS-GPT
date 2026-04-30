# config
MAX_PERIODS = MAX_LANDSAT = MAX_SENTINEL2 = 366
FILL_VALUE = -9999.
MASK_VALUE = -9999.
lst = []
L8_fields = []
S2_fields = []
use_tir = False

# L8_fields.append('year')
for i in range(MAX_PERIODS):
    lst.append(f'L{i:03d}.coastal')
    lst.append(f'L{i:03d}.blue')
    lst.append(f'L{i:03d}.green')
    lst.append(f'L{i:03d}.red')
    lst.append(f'L{i:03d}.nir')
    lst.append(f'L{i:03d}.swir1')
    lst.append(f'L{i:03d}.swir2')
    lst.append(f'L{i:03d}.bt1')
    lst.append(f'L{i:03d}.bt2')
    lst.append(f'L{i:03d}.qa')
    lst.append(f'L{i:03d}.doy')
    
    L8_fields.append(f'L{i:03d}.doy'    )
    L8_fields.append(f'L{i:03d}.coastal')
    L8_fields.append(f'L{i:03d}.blue'   )
    L8_fields.append(f'L{i:03d}.green'  )
    L8_fields.append(f'L{i:03d}.red'    )
    L8_fields.append(f'L{i:03d}.nir'    )
    L8_fields.append(f'L{i:03d}.swir1'  )
    L8_fields.append(f'L{i:03d}.swir2'  )
    if use_tir:
        L8_fields.append(f'L{i:03d}.bt1')
        L8_fields.append(f'L{i:03d}.bt2')

# S2_fields.append('year')
START_I_REF = 1 
for i in range(MAX_PERIODS):
    lst.append(f'S{i:03d}.coastal')
    lst.append(f'S{i:03d}.blue')
    lst.append(f'S{i:03d}.green')
    lst.append(f'S{i:03d}.red')
    lst.append(f'S{i:03d}.edge1')
    lst.append(f'S{i:03d}.edge2')
    lst.append(f'S{i:03d}.edge3')
    lst.append(f'S{i:03d}.nir8')
    lst.append(f'S{i:03d}.nirA')
    lst.append(f'S{i:03d}.swir1')
    lst.append(f'S{i:03d}.swir2')
    lst.append(f'S{i:03d}.qa')
    lst.append(f'S{i:03d}.doy')
    
    S2_fields.append(f'S{i:03d}.doy'    )
    S2_fields.append(f'S{i:03d}.coastal')
    S2_fields.append(f'S{i:03d}.blue'   )
    S2_fields.append(f'S{i:03d}.green'  )
    S2_fields.append(f'S{i:03d}.red'    )
    S2_fields.append(f'S{i:03d}.nirA'   )
    S2_fields.append(f'S{i:03d}.swir1'  )
    S2_fields.append(f'S{i:03d}.swir2'  )
    S2_fields.append(f'S{i:03d}.edge1'  )
    S2_fields.append(f'S{i:03d}.edge2'  )
    S2_fields.append(f'S{i:03d}.edge3'  )
    S2_fields.append(f'S{i:03d}.nir8'   )

