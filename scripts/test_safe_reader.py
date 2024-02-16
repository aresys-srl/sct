# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SAFE product reader testing script"""

from arepyextras.quality.io.quality_input_protocol import (
    ChannelData,
    QualityInputProduct,
)

from sct.io.quality_input_from_sentinel1_product import Sentinel1ProductManager

if __name__ == "__main__":
    pt = r"C:\Users\giorgio.parma\Aresys_DATA\SAFE products\S1A_IW_SLC__1SSH_20190108T083240_20190108T083310_025383_02CF92_AB14.SAFE"
    pt = r"C:\Users\giorgio.parma\Aresys_DATA\SAFE products\S1A_IW_GRDH_1SSH_20190108T083240_20190108T083309_025383_02CF92_BD04.SAFE"
    prod = Sentinel1ProductManager(path=pt)
    assert isinstance(prod, QualityInputProduct)
    print(prod.name)
    print(prod.channels_list)
    channel = prod.get_channel_data(prod.channels_list[0])
    assert isinstance(channel, ChannelData)
    img = channel.read_data(1150, 2310)
    pass
