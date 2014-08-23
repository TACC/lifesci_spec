-- $Id$ --

-------------------------------------------------------------------------
--   Test code for using  Dbg.lua
-------------------------------------------------------------------------

--    require("strict")
--    require("Dbg")
--    function a()
--       local dbg   = Dbg:dbg()
--       dbg.start(2,"a")
--       dbg.print("In a","\n")
--       b()
--       dbg.fini()
--    end
--    
--    function b()
--       local dbg   = Dbg:dbg()
--       dbg.start(2,"b")
--       dbg.print("In b","\n")
--       c()
--       dbg.fini()
--    end
--    
--    function c()
--       local dbg   = Dbg:dbg()
--       dbg.start(3,"c")
--       dbg.print(1,"In c","\n")
--       dbg.fini()
--    end
--    
--    function main()
--       local level = 10
--       local dbg   = Dbg:dbg()
--       dbg:activateDebug(level)
--    
--       dbg.start(2,"main")
--       a()
--       dbg.fini()
--    end
--    
--    main()

local blank        = " "
local huge         = math.huge
local io           = io
local ipairs       = ipairs
local max          = math.max
local os           = os
local select       = select
local setmetatable = setmetatable
local tostring     = tostring
local type         = type
local remove       = table.remove

require("strict")

--module("Dbg")
local M = {}

s_dbg           = nil
s_warningCalled = false
s_indentString  = ""
s_indentLevel   = 0
s_vpl           = 1
s_currentLevel  = huge
s_levelA        = {}
s_isActive      = false
s_prefix        = ""
local function prtTbl(a)
   io.stderr:write("table:\n")
   for _,v in ipairs(a) do
      if (type(a) == "table") then
	 prtTbl(v)
      else
	 io.stderr:write(v)
      end
   end
end

local function new(self)
   local o = {}
   setmetatable(o,self)
   self.__index = self
   o.print      = M.Quiet
   o.start      = M.Quiet
   o.fini       = M.Quiet
   o.warning    = M.Warning
   o.error      = M.Error
   o.quiet      = M.Quiet
   o.indent     = M.Empty
   o.is_active  = false
   --if (t and type(t) == 'table') then
   --   o.vpl       = t.vpl
   --end
   return o
end

function M.dbg(self)
   if (s_dbg == nil) then
      s_dbg = new(self)
   end
   return s_dbg
end

function M.set_prefix(prefix)
   s_prefix = prefix .. " "
end

function M.activateDebug(self, level)
   level = level or 1
   if (level > 0) then
      self.print            = M.Debug
      self.start            = M.Start
      self.fini             = M.Fini
      self.indent           = M.Indent
      s_isActive            = true
      s_currentLevel        = level
      s_levelA[#s_levelA+1] = level
   end
end

function M.active()
   return s_isActive
end

function M.currentLevel(level)
   s_currentLevel = level or 1
end

function M.deactivateWarning(self)
   self.warning = M.Quiet
end

function M.activateWarning(self)
   self.warning = M.Warning
end

function M.Quiet()
end

local function extractVPL(...)
   local vpl = s_vpl
   local firstV = select(1,...)
   if (type(firstV) == "number") then
      vpl = firstV
   end
   return vpl
end   

local function startExtractVPL(...)
   local vpl = s_vpl
   local firstV = select(1,...)
   if (type(firstV) == "number") then
      vpl = firstV
   end
   s_levelA[#s_levelA+1] = vpl
   return vpl
end   

function M.Start(...)
   s_vpl = startExtractVPL(...)
   if (s_vpl <= s_currentLevel) then 
      io.stderr:write(s_indentString)
      for i,v in ipairs{...} do
         if (i ~= 1 or type(v) ~= "number") then
            io.stderr:write(v)
         end
      end
      io.stderr:write("{\n")
      s_indentLevel  = s_indentLevel + 1
      s_indentString = blank:rep(s_indentLevel*2)
   end
end

function M.Empty()
   return ""
end

function M.Indent()
   return blank:rep(s_indentLevel*2)
end

function M.Fini()
   local vpl = s_vpl
   if (#s_levelA > 1) then
      remove(s_levelA)  -- remove last entry in table
   end
   s_vpl = s_levelA[#s_levelA]

   if (vpl <= s_currentLevel) then 
      s_indentLevel  = max(0, s_indentLevel - 1)
      s_indentString = blank:rep(s_indentLevel*2)
      io.stderr:write(s_indentString,"}\n")
   end
end

function M.Warning(...)
   io.stderr:write("\n",s_prefix,"Warning: ")
   for _,v in ipairs{...} do
      io.stderr:write(v)
   end
   s_warningCalled = true
end

function M.Error(...)
   io.stderr:write("\n",s_prefix,"Error: ")
   for _,v in ipairs{...} do
      io.stderr:write(v)
   end
   io.stderr:write("\n")
   errorExit()
end

function M.errorExit()
   io.stdout:write("false\n")
   os.exit(1)
end
   
function M.warningCalled()
   return s_warningCalled
end


function M.Debug(...)
   local vpl = extractVPL(...)
   if (vpl > s_currentLevel) then 
      return 
   end

   io.stderr:write(s_indentString)
   for i,v in ipairs{...} do
      if (type(v) == "table") then
	 prtTbl(v)
      elseif (i == 1 and type(v) == 'number') then
         -- do nothing
      else
         if (type(v) ~= "string") then
            v = tostring(v)
         end
         local idx = v:find("\n")
         if (idx == nil or v:len() == idx) then
            io.stderr:write(v)
         else
            local s = v:sub(1,idx)
            io.stderr:write(s)
            M.Debug(v:sub(idx+1))
         end
      end
   end
end

function M.flush()
   io.stderr:flush()
end

return M
