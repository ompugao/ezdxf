# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING
from .dxfentity import DXFEntity, SubclassProcessor, DXFNamespace
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF2004, DXF2000

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, ExtendedTags, TagWriter

__all__ = ['DXFClass']

dxfclass_class = DefSubclass(None, {
    # Class DXF record name; always unique
    'name': DXFAttr(1),
    # C++ class name. Used to bind with software that defines object class behavior; always unique
    'cpp_class_name': DXFAttr(2),
    # Application name. Posted in Alert box when a class definition listed in this section is not currently loaded
    'app_name': DXFAttr(3),
    # Proxy capabilities flag. Bit-coded value that indicates the capabilities of this object as a proxy:
    # 0 = No operations allowed (0)
    # 1 = Erase allowed (0x1)
    # 2 = Transform allowed (0x2)
    # 4 = Color change allowed (0x4)
    # 8 = Layer change allowed (0x8)
    # 16 = Linetype change allowed (0x10)
    # 32 = Linetype scale change allowed (0x20)
    # 64 = Visibility change allowed (0x40)
    # 128 = Cloning allowed (0x80)
    # 256 = Lineweight change allowed (0x100)
    # 512 = Plot Style Name change allowed (0x200)
    # 895 = All operations except cloning allowed (0x37F)
    # 1023 = All operations allowed (0x3FF)
    # 1024 = Disables proxy warning dialog (0x400)
    # 32768 = R13 format proxy (0x8000)
    'flags': DXFAttr(90, default=0),
    # Instance count for a custom class
    'instance_count': DXFAttr(91, dxfversion=DXF2004, default=0),
    # Was-a-proxy flag. Set to 1 if class was not loaded when this DXF file was created, and 0 otherwise
    'was_a_proxy': DXFAttr(280, default=0),
    # Is-an-entity flag. Set to 1 if class was derived from the AcDbEntity class and can reside in the BLOCKS or
    # ENTITIES section. If 0, instances may appear only in the OBJECTS section
    'is_an_entity': DXFAttr(281, default=0),
})


class DXFClass(DXFEntity):
    DXFTYPE = 'CLASS'
    DXFATTRIBS = DXFAttributes(dxfclass_class)

    @classmethod
    def new(cls, handle: str = None, owner: str = None, dxfattribs: dict = None, doc: 'Drawing' = None) -> 'DXFClass':
        """ New CLASS constructor - has no handle, no owner and do not need document reference """
        dxfclass = cls()
        dxfclass.update_dxf_attribs(dxfattribs)
        return dxfclass

    def load_tags(self, tags: 'ExtendedTags') -> None:
        """ Called by load constructor. CLASS is special. """
        if tags:
            # do not process base class!!!
            self.dxf = DXFNamespace(entity=self)
            processor = SubclassProcessor(tags)
            processor.load_dxfattribs_into_namespace(self.dxf, dxfclass_class)

    def export_dxf(self, tagwriter: 'TagWriter'):
        """ Do all, because CLASS is special. """
        dxfversion = tagwriter.dxfversion
        if dxfversion < DXF2000:
            return
        attribs = self.dxf
        tagwriter.write_tag2(0, self.DXFTYPE)
        attribs.export_dxf_attribs(tagwriter, ['name', 'cpp_class_name', 'app_name', 'flags'])
        if dxfversion >= DXF2004:
            # required, but can always be 0
            attribs.export_dxf_attribute(tagwriter, 'instance_count', force=True)
        attribs.export_dxf_attribs(tagwriter, ['was_a_proxy', 'is_an_entity'])
