from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup

inventario=[   
    {'codigo': '111', 'nombre': 'leche 1L', 'precio': 4000, 'cantidad': 20},
	{'codigo': '222', 'nombre': 'cereal 500g', 'precio': 8000, 'cantidad': 15}, 
	{'codigo': '333', 'nombre': 'yogurt 1L', 'precio': 9000, 'cantidad': 10},
	{'codigo': '444', 'nombre': 'helado 2L', 'precio': 1000, 'cantidad': 20},
	{'codigo': '555', 'nombre': 'alimento para perro 20kg', 'precio': 50000, 'cantidad': 5},
	{'codigo': '666', 'nombre': 'shampoo', 'precio': 8000, 'cantidad': 25},
	{'codigo': '777', 'nombre': 'papel higiénico 4 rollos', 'precio': 8000, 'cantidad': 30},
	{'codigo': '888', 'nombre': 'jabón para trastes', 'precio': 8500, 'cantidad': 5},
	{'codigo': '999', 'nombre': 'refresco 600ml', 'precio': 5500, 'cantidad': 10},
    {'codigo': '1111', 'nombre': 'Paquete de leches x4', 'precio': 25000, 'cantidad': 10},
    {'codigo': '2222', 'nombre': 'Condones paquete 3', 'precio': 12000, 'cantidad': 10}
]


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    touch_deselect_last = BooleanProperty(True)                                    #Es para que solo pueda seleccionar un producto al mismo tiempo


class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad_carrito'])
        self.ids['_precio_por_articulo'].text = str("{:.0f}".format(data['precio']))
        self.ids['_precio'].text = str("{:.0f}".format(data['precio_total']))
        return super(SelectableBoxLayout, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayout, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Responde a la selección de los productos. '''
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']= True
        else:
            rv.data[index]['seleccionado']= False


class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    ''' Se agrega la seleccion del layout popup para la seleccion de producto. '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_codigo'].text = data['codigo']
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio'].text = str("{:.0f}".format(data['precio']))
        return super(SelectableBoxLayoutPopup, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayoutPopup, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Función que determina si el producto esta seleccionado o no. '''
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']= True
        else:
            rv.data[index]['seleccionado']= False

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []
        self.modificar_producto= None

    def agregar_articulo(self, articulo):
        articulo['seleccionado']=False
        indice = -1
        if self.data:
            for i in range(len(self.data)):
                if articulo['codigo']==self.data[i]['codigo']:
                    indice = i 
            if indice >= 0:
                self.data[indice]['cantidad_carrito']+=1
                self.data[indice]['precio_total']= self.data[indice]['precio']*self.data[indice]['cantidad_carrito']
                self.refresh_from_data()
            else:
                self.data.append(articulo)
        else:
            self.data.append(articulo)
            
    def articulo_seleccionado(self):
        """Self.data seleccionado"""
        indice = -1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice = i
                break
        return indice
    
    def eliminar_articulo(self):
        """Se utiliza para eliminar el articulo y tambien restar al total del carrito"""
        indice = self.articulo_seleccionado()
        precio = 0                                                                                                                  
        if indice >= 0:
            self._layout_manager.deselect_node(self.layout_manager._last_selected_node)                                             #Esto es un comando de kivy el cual nos deseleccionara la casilla despues de eliminar el anterior articulo
            precio = self.data[indice]['precio_total']                                                                              #Nos regresara el precio total del producto seleccionado 
            self.data.pop(indice)                                                                                                   #Eliminara de la lista de la lista self.data el articulo que este en el indice
            self.refresh_from_data()
        return precio                                                                                                               #Este es el valor que recibira la función eliminar_producto             
    
    def modificar_articulo(self):
        indice = self.articulo_seleccionado()                                                                                       #Aqui solo nos va a ubicar dentro de la lista self.data cual es el articulo que esta seleccionado
        if indice >= 0:                                                                                                              #Nos indicara si hay o no un producto seleccionado
            popup = CambiarCantidadPopup(self.data[indice], self.actualizar_articulo)                                                                          #El self.data es para proporcionar informacion del producto
            popup.open()
            
            
    def actualizar_articulo(self, valor):
        """Aqui es donde se le cambia la cantidad al articulo por individual"""
        indice = self.articulo_seleccionado()
        if indice >= 0:
            if valor == 0:                                                                                                            #Si el valor del producto es 0 significa que se va a borrar
                self.data.pop(indice)                                                                                                 #El pop es para borrar el producto 
                self.layout_manager.deselect_node(self._layout_manager._last_selected_node)
            else:
                self.data[indice]['cantidad_carrito']=valor
                self.data[indice]['precio_total']= self.data[indice]['precio']*valor                                             #el indice lo multiplicamos la cantidad de productos para que de el nuevo precio total 
            self.refresh_from_data()                                                                                                     #Esta linea es para refrescar el indicador de precio 
            nuevo_total = 0
            for data in self.data:
                nuevo_total += data['precio_total']
            self.modificar_producto(False, nuevo_total)                                                                              #Se asigna una nueva variable para cambiar el subtotal
            
class ProductoPorNombrePopup(Popup):
    def __init__(self, input_nombre, agregar_producto_callback, **kwargs):
        super(ProductoPorNombrePopup, self).__init__(**kwargs)
        self.input_nombre=input_nombre  
        self.agregar_producto=agregar_producto_callback
        
    def mostrar_articulos(self):
        self.open()
        for nombre in inventario:
            if nombre['nombre'].lower().find(self.input_nombre)>= 0:
                producto={'codigo': nombre['codigo'], 'nombre': nombre['nombre'], 'precio': nombre['precio'], 'cantidad': nombre['cantidad']}
                self.ids.rvs.agregar_articulo(producto)
                
    def seleccionar_articulo(self):
        indice = self.ids.rvs.articulo_seleccionado()
        if indice >= 0:
            _articulo=self.ids.rvs.data[indice]
            articulo={}
            articulo['codigo']=_articulo['codigo']
            articulo['nombre']=_articulo['nombre']
            articulo['precio']=_articulo['precio']
            articulo['cantidad_carrito']=1
            articulo['cantidad_inventario']=_articulo['cantidad']
            articulo['precio_total']=_articulo['precio']
            if callable(self.agregar_producto):
                self.agregar_producto(articulo)
            self.dismiss()

class CambiarCantidadPopup(Popup):                                                                                                   #Se declaro la clase para generar un popup al cambiar la cantidad
    def __init__(self,data,actualizar_articulo_callback, **kwargs):
        super(CambiarCantidadPopup, self).__init__(**kwargs)
        self.data = data    
        self.actualizar_articulo= actualizar_articulo_callback
        self.ids.info_nueva_cant_1.text = "Producto: " + self.data['nombre'].capitalize()                                              #Es para asignarle el nombre del producto en el popup
        self.ids.info_nueva_cant_2.text = "Cantidad: " + str(self.data['cantidad_carrito'])                                                 #Es para asignar la cantidad que tenemos en el carrito
        
    def validar_input(self, texto_input):                                                                                                              #Aqui se define la funcion para validar lo que pone el usuario
        try:
            nueva_cantidad = int(texto_input)                                                                                         #Validar si solo son enteros lo que ingreso el usuario
            self.ids.notificacion_no_valido.text=''
            self.actualizar_articulo(nueva_cantidad)                                                                                    #Esta linea es para cambiar la cantidad si los datos estan bien
            self.dismiss()
        except:
            self.ids.notificacion_no_valido.text='Cantidad no valida'

class PagarPopup(Popup):                                                                                                   #Se declaro la clase para generar un popup al cambiar la cantidad
    def __init__(self, total, **kwargs):
        super(PagarPopup, self).__init__(**kwargs)
        self.total = total
    
class VentasWindow(BoxLayout):
    """Se dan las funciones para los botones de las ventanaswindow"""
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.total= 0
        self.ids.rvs.modificar_producto = self.modificar_producto
        
    def agregar_producto_codigo(self, codigo):
        for producto in inventario: 
            if codigo==producto['codigo']:
                articulo={}
                articulo['codigo']=producto['codigo']
                articulo['nombre']=producto['nombre']
                articulo['precio']=producto['precio']
                articulo['cantidad_carrito']=1
                articulo['cantidad_inventario']=producto['cantidad']
                articulo['precio_total']=producto['precio']
                self.agregar_producto(articulo)
                self.ids.buscar_codigo.text=''
                break
        
    def agregar_producto_nombre(self, nombre):
        self.ids.buscar_nombre.text=''
        popup=ProductoPorNombrePopup(nombre, self.agregar_producto)
        popup.mostrar_articulos()
        
    def agregar_producto(self,articulo):
        self.total+=articulo['precio']
        self.ids.sub_total.text= '$'+"{:.0f}".format(self.total)
        self.ids.rvs.agregar_articulo(articulo)
        
    def eliminar_producto(self):
        menos_precio = self.ids.rvs.eliminar_articulo()                                                                               #Se hace para saber cuanto se le quitara al self.total                                                      
        self.total -= menos_precio                                                                                                    #Esta operacion es para quitar valor del producto seleecionado
        self.ids.sub_total.text = '$'+"{:.0f}".format(self.total)                                                                     #Se formatea el total nuevo para que se realicen los cambios en la parte visual
        
    def modificar_producto(self, cambio = True, nuevo_total = None):
        if cambio:
            self.ids.rvs.modificar_articulo()
        else:
            self.total = nuevo_total
            self.ids.sub_total.text = '$'+"{:.0f}".format(self.total)
        
    def pagar(self):
        if self.ids.rvs.data:
            popup=PagarPopup(self.total)
            popup.open()
        else:
            self.ids.notificacion_falla.text='No hay nada que pagar'
            
    def nueva_compra(self):
        print("nueva compra")
    
          
    def admin(self):
        print("Admin presionado")
        
    def signout(self):
        print("Sign out presionado")
        
        

class VentasApp(App):
    def build(self):
        return VentasWindow()
    
if __name__ == '__main__':
    VentasApp().run()
    

        
    