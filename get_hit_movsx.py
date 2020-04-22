from idc import *
from idautils import *
import idaapi

'''
    This will grab all our movsx lines hit by an ablation run and poop it into a window
'''

movsx = []
color = 0x7BF0D3 #ablation mark color

class HitfuncViewer(idaapi.simplecustviewer_t):
    def __init__(self, data):
        self.hitfuncs = data
        self.Create()
        print "Launching ablation hit function subview..."
        self.Show()

    def Create(self):
        title = "Hit Functions"
        idaapi.simplecustviewer_t.Create(self, title)
        
        comment = idaapi.COLSTR("#### Double-click to follow ####", idaapi.SCOLOR_BINPREF)
        self.AddLine(comment)
        self.AddLine("")

        for s in self.hitfuncs:
            line = idaapi.COLSTR("%s:" % s['name'], idaapi.SCOLOR_BINPREF)
            self.AddLine(line)
            for addr in s['src']:
                line = idaapi.COLSTR("    %s" % addr, idaapi.SCOLOR_INSN)
                self.AddLine(line)
            self.AddLine("")

        return True

    def OnDblClick(self, something):
        line = self.GetCurrentLine()
        if "0x" not in line:
            name = line[2: line.find(":")]
            segbeg = SegByName(".text")
            segend = SegEnd(segbeg)
            for ea in Functions(segbeg, segend):
                fname = GetFunctionName(ea)
                if fname == name:
                    Jump(ea)
                    return True
            return False
        idx = line.find("0x")
        addy = int(line[idx: idx+10], 16)
        Jump(addy)
        return True

    def OnHint(self, lineno):
#        if lineno < 2: return False
#        else: lineno -= 2
#        line = self.GetCurrentLine()
#        if "0x" not in line: return False
#
#        addy = int(line[2:line.find(":")], 16)
#        disasm = idaapi.COLSTR(GetDisasm(addy) + "\n", idaapi.SCOLOR_DREF)
#        return (1, disasm)
        return False




segbeg = SegByName(".text")
segend = SegEnd(segbeg)
for ea in Functions(segbeg, segend):
    funcname = GetFunctionName(ea)
    beg = ea
    end = FindFuncEnd(beg)
    src = []
    curea = beg
    
    while curea <= end and curea != BADADDR:
        mnem = GetMnem(curea)
        if 'movsx' in mnem:
            if (GetColor(curea, 1) == color):
                src.append("0x%08x" % curea)

        curea = NextHead(curea, end)
    if len(src) > 0:
        movsx.append({'name': funcname, 'src': src})

HitfuncViewer(sorted(movsx))
