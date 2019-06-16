from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase
import time
import unittest

class Visitante(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_puede_ingresar_nuevo_paciente(self):
        #Pia Quintanilla quiere ingresar los datos de un paciente
        #para ello, ingresa a:
        self.browser.get('http://localhost:8000')

        #Nota el nombre de la página
        self.assertIn('Clínica Dental Mauricio Dr. Mauricio Martínez', self.browser.title)

        #Y ve la página de Inicio
        self.assertIn('Inicio', self.browser.find_element_by_tag_name('h1').text)
        #Luego hace clic en botón Nuevo Paciente en el menú

        #Finalmente Pía cierra el navegador
        self.fail('¡Termina el test!')
        browser.quit()
