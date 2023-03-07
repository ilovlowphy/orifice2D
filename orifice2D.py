## this app is used to create corifce2D mesh. the application is pointwise.
from pointwise import GlyphClient
from math import ceil
# from pointwise.glyphaself.pi import *




def echo(line):
  print("Script: {0}".format(line), end='')  # Not Python 2.7 compatible


def sum_rate(n,rate):
  sum = 0
  for i in range(n):
    sum+=rate**i
  return sum


def get_grow_num(init_spacing,grow_rate,max_spacing):
  num = 0
  height = init_spacing
  while(height<max_spacing):
    height*=grow_rate
    num+=1
  return num


def from_total_get_num(init_spacing,grow_rate,total):
  num = 0
  total_height = init_spacing
  while(total_height<total):
    total_height=init_spacing*sum_rate(num+1,grow_rate)
    num+=1
  return num

class Orifice2D:
  def __init__(self,beta,init_spacing = 0.3,thick=0,diameter = 100, front_num_of_D = 10,back_num_of_D= 5,max_spacing=0,grow_rate=1.1):
    self.beta = beta
    self.init_spacing=init_spacing
    self.thick = thick
    self.diameter =diameter
    self.front_num_of_D = front_num_of_D
    self.back_num_of_D = back_num_of_D
    self.init_server()
    if(max_spacing==0):
      self.max_spacing = self.diameter/50
    else:
      self.max_spacing = max_spacing
    self.grow_rate = grow_rate
    # self.grow_layer_number = grow_layer_number

  def init_server(self):
    # Connect to the Pointwise server listening on localhost at the default port
    # with no authentication token...

    # glf = GlyphClient()

    # ... or create a pointwise server as a subprocess and connect to that.
    # Note: this will consume a Pointwise license


    
    # Run in batch mode
    # glf = GlyphClient(port=0, callback=echo)

    # Run in GUI, default port
    self.glf = GlyphClient(callback=echo)

    self.glf.connect()

    # Use the Glyph Aself.pi for Python
    self.pw = self.glf.get_glyphapi()

    # Allow error messages to be printed on the server
    self.pw.Database._setVerbosity("Errors")
    self.pw.Application._setVerbosity("Errors")

    # Reset the server's workspace
    self.pw.Application.reset()
    self.pw.Application.clearModified()

    # set the solver
    self.pw.Application.setCAESolver("ANSYS Fluent",2)





  def set_connector(self,con,max_spacing=0,begin=False,end=False,init_spacing=0,grow_rate=0):
    total_length = con.getTotalLength()
    if(max_spacing==0):
      max_spacing=self.max_spacing
    if(init_spacing==0):
      init_spacing = self.init_spacing
    if(grow_rate==0):
      grow_rate = self.grow_rate

    # while the begin and end setting no spacing
    if(not(begin or end)):
      total_num=ceil(total_length/max_spacing)
      con.setDimension(total_num+1)
      return
    
    begin_num = get_grow_num(init_spacing,grow_rate,max_spacing) if begin else 0
    begin_length = self.init_spacing*sum_rate(begin_num,grow_rate) if begin else 0

    end_num = get_grow_num(init_spacing,grow_rate,max_spacing) if end else 0
    end_length = self.init_spacing*sum_rate(end_num,grow_rate) if end else 0

    
    middle_length = total_length - begin_length - end_length
    # self.glf.puts("%.2f" % (middle_length))

    if(middle_length<0):
      if(begin and end):
        total_num = from_total_get_num(init_spacing,grow_rate,total_length/2) * 2
        con.getDistribution(1).setBeginSpacing(init_spacing)
        con.getDistribution(1).setEndSpacing(init_spacing)
        con.setDimension(total_num+1)
        return
      elif(begin):
        total_num = from_total_get_num(init_spacing,grow_rate,total_length)
        con.getDistribution(1).setBeginSpacing(init_spacing)
        con.setDimension(total_num+1)
        return
      elif(end):
        total_num = from_total_get_num(init_spacing,grow_rate,total_length)
        con.getDistribution(1).setEndSpacing(init_spacing)
        con.setDimension(total_num+1)
        return
    else:
      middle_num = ceil(middle_length/max_spacing)
      total_num = begin_num+end_num+middle_num
      con.replaceDistribution(1,self.pw.DistributionGrowth.create())
      if(begin):
        con.getDistribution(1).setBeginSpacing(self.init_spacing)
        con.getDistribution(1).setBeginMode("LayersAndRate")
        con.getDistribution(1).setBeginLayers(begin_num)
        con.getDistribution(1).setBeginRate(grow_rate)
      if(end):
        con.getDistribution(1).setEndSpacing(self.init_spacing)
        con.getDistribution(1).setEndMode("LayersAndRate")
        con.getDistribution(1).setEndLayers(end_num)
        con.getDistribution(1).setEndRate(grow_rate)
      con.setDimension(total_num+1)



  def run(self):
    # pw::Connector setDefault Dimension 30
    # pw.Connector.setDefault("Dimension", 30)

    # set default spacing as 3
    self.pw.Connector.setCalculateDimensionMethod("Spacing")
    self.pw.Connector.setCalculateDimensionSpacing(self.diameter/100)
    self.pw.Connector.setCalculateDimensionMaximum(1024)

    # caculate the base length
    if(self.thick==0):
      self.thick = 0.02*self.diameter
    self.front_length = self.front_num_of_D*self.diameter
    self.back_length = self.back_num_of_D*self.diameter
    self.orifice_diamter = self.diameter* self.beta

    # set the base points
    ## inlet position
    self.pi1 = (-self.front_length, self.diameter/2, 0)
    self.pi2 = (-self.front_length, self.orifice_diamter/2,0)
    self.pi3 = (-self.front_length, 0, 0)
    ## orifice front face
    self.pof1 = (-self.thick, self.diameter/2, 0)
    self.pof2 = (-self.thick, self.orifice_diamter/2,0)
    self.pof3 = (-self.thick, 0, 0)
    ## orifice back face
    self.pob1 = (0, self.diameter/2, 0)
    self.pob2 = (0, self.orifice_diamter/2,0)
    self.pob3 = (0, 0, 0)
    ## outlet position
    self.po1 = (self.back_length, self.diameter/2, 0)
    self.po2 = (self.back_length, self.orifice_diamter/2,0)
    self.po3 = (self.back_length, 0, 0)

    # create connector
    ## inlet position
    self.ci1 = self.create_connector(self.pi1,self.pi2)
    self.ci2 = self.create_connector(self.pi2,self.pi3)
    ## orifice front face
    self.cof1 = self.create_connector(self.pof1,self.pof2)
    self.cof2 = self.create_connector(self.pof2,self.pof3)
    ## orifice back face
    self.cob1 = self.create_connector(self.pob1,self.pob2)
    self.cob2 = self.create_connector(self.pob2,self.pob3)
    ## outlet position
    self.co1 = self.create_connector(self.po1,self.po2)
    self.co2 = self.create_connector(self.po2,self.po3)
    ## between inlet and orifice front
    self.ci2of1 = self.create_connector(self.pi1,self.pof1)
    self.ci2of2 = self.create_connector(self.pi2,self.pof2)
    self.ci2of3 = self.create_connector(self.pi3,self.pof3)
    ## between orfice front and orifice back
    self.cof2ob2 = self.create_connector(self.pof2,self.pob2)
    self.cof2ob3 = self.create_connector(self.pof3,self.pob3)
    ## between orfice back and outlet
    self.cob2o1 = self.create_connector(self.pob1,self.po1)
    self.cob2o2 = self.create_connector(self.pob2,self.po2)
    self.cob2o3 = self.create_connector(self.pob3,self.po3)

    self.cc1 = (self.ci1,self.cof1,self.cob1,self.co1)
    self.cc2 = (self.ci2,self.cof2,self.cob2,self.co2)

    self.cci2of = (self.ci2of1,self.ci2of2,self.ci2of3)
    self.ccof2ob = (self.cof2ob2,self.cof2ob3)
    self.ccob2o = (self.cob2o1,self.cob2o2,self.cob2o3)
    
    for i in self.cc1:
      self.set_connector(i,self.max_spacing,True,True)
    for i in self.cc2:
      self.set_connector(i,self.max_spacing,True,False)
    for i in self.cci2of:
      self.set_connector(i,self.max_spacing,False,True,grow_rate=1.02)
    for i in self.ccof2ob:
      self.set_connector(i,self.init_spacing)
    for i in self.ccob2o:
      self.set_connector(i,self.max_spacing,True,False,grow_rate=1.02)

    # domain 
    self.di2of1 = self.pw.DomainStructured.createFromConnectors(solid=(self.ci1,self.ci2of2,self.cof1,self.ci2of1))
    self.di2of2 = self.pw.DomainStructured.createFromConnectors(solid=(self.ci2,self.ci2of3,self.cof2,self.ci2of2))
    self.dof2ob2 = self.pw.DomainStructured.createFromConnectors(solid=(self.cof2,self.cof2ob3,self.cob2,self.cof2ob2))
    self.dob2o1 = self.pw.DomainStructured.createFromConnectors(solid=(self.cob1,self.cob2o2,self.co1,self.cob2o1))
    self.dob2o2 = self.pw.DomainStructured.createFromConnectors(solid=(self.cob2,self.cob2o3,self.co2,self.cob2o2))
    self.domains = [self.di2of1,self.di2of2,self.dof2ob2,self.dob2o1,self.dob2o2]

    self.create_boundary()
    self.pw.Application.export(self.domains, "aa.cas", precision="Double")
    self.glf.close()

  def create_connector(self,p1,p2):
    with self.pw.Application.begin("Create") as creator:
      # set seg [pw::SegmentSpline create]
      seg = self.pw.SegmentSpline()

      # $seg addPoint {0 0 0}
      seg.addPoint(p1)
      seg.addPoint(p2)

      # set con [pw::Connector create]
      con = self.pw.Connector()

      # $con addSegment $seg
      con.addSegment(seg)

      # $con calculateDimension
      con.calculateDimension()
      return con


      # "$creator end" is implied
  def create_boundary(self):
    # inlet
    inlet_bc_list = [[self.di2of1,self.ci1],[self.di2of2,self.ci2]]
    self.inlet_BC = self.pw.BoundaryCondition()
    self.inlet_BC.setName("inlet")
    self.inlet_BC.setPhysicalType("Velocity Inlet",usage="CAE")
    self.inlet_BC.apply(inlet_bc_list)
    # wall
    wall_bc_list = [[self.di2of1,self.ci2of1],[self.di2of1,self.cof1],[self.dof2ob2,self.cof2ob2],[self.dob2o1,self.cob1],[self.dob2o1,self.cob2o1]]
    self.wall_BC = self.pw.BoundaryCondition()
    self.wall_BC.setName("wall")
    self.wall_BC.setPhysicalType("Wall",usage="CAE")
    self.wall_BC.apply(wall_bc_list)
    # outlet
    outlet_bc_list = [[self.dob2o1,self.co1],[self.dob2o2,self.co2]]
    self.outlet_BC = self.pw.BoundaryCondition()
    self.outlet_BC.setName("outlet")
    self.outlet_BC.setPhysicalType("Pressure Outlet",usage="CAE")
    self.outlet_BC.apply(outlet_bc_list)
    # axis
    axis_bc_list = [[self.di2of2,self.ci2of3],[self.dof2ob2,self.cof2ob3],[self.dob2o2,self.cob2o3]]
    self.axis_BC = self.pw.BoundaryCondition()
    self.axis_BC.setName("axis")
    self.axis_BC.setPhysicalType("Axis",usage="CAE")
    self.axis_BC.apply(axis_bc_list)

    self.volum = self.pw.VolumeCondition()
    self.volum.setName("fluid")
    self.volum.setPhysicalType("Fluid")
    self.volum.apply(self.domains)



if(__name__=="__main__"):
  orifice = Orifice2D(0.3)
  orifice.run()
