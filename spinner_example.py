import param
import panel as pn 
import time
pn.extension(loading_spinner='bar') # valid options for loading indicators are ‘arc’, ‘arcs’, ‘bar’, ‘dots’, ‘petal’

class Gizmo(param.Parameterized):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.param.watch(
            self._execute, 
            [k for k, v in self.param.objects().items()], 
            queued=True,
        )

    def _execute(self, *_events):
        """
        wrapper for the execute function.  
        """

        # If the __panel__  generated a layout then set the busy indicator
        #
        if '_layout' in self.__dict__:
            self._layout.busy_indicator.value = True

        try:
            self.execute()
        
        finally:

            if '_layout' in self.__dict__:
                self._layout.busy_indicator.value = False
            

    def execute(self):
        pass


    def __panel__(self):
        """
        __panel__ creates a layout and saves it. Saving a reference to the created 
        panel layout allows us to do update the loading state later on. Not sure 
        what we want to do if the developer wants to overwrite the presentation layer. 
        """

        self._layout = pn.Param(self.param)
        # self._layout.busy_indicator = param.Boolean(default=False)
        self._layout.busy_indicator = pn.indicators.LoadingSpinner(height=20, width=20)
        
        return self._layout


class A(Gizmo):

    out_1 = param.Number(default=0)
    out_2 = param.Number(default=0)
    run = param.Event()


    def execute(self):
        """ This runs on param change so we have to manually check for the Event and
        switch it back if we want to. 
        """

        # This bit is kind of awkward, we have to check the status of the launch event
        # and set it back at the end to avoid continuously trigger execute
        #
        if self.run:

            # print(f'{self.loading=}')

            print('Incrementing A.out_1')
            self.out_1 += 1

            time.sleep(3)
            
            print('Incrementing A.out_2')
            self.out_2 = self.out_1 + 1

            # Without this we're stuck in an infinite loop
            # 
            self.run = False


class B(Gizmo):

    in_1 = param.Number(default=0, allow_refs=True)
    in_2 = param.Number(default=0, allow_refs=True)
    out_3 = param.Number(default=0)

    def execute(self):

        print(f'B.in_1={self.in_1}')
        
        time.sleep(3)
        
        print(f'B.in_2={self.in_2}')
        
        self.out_3 = self.in_1 + self.in_2
        
        print(f'B.out_3={self.out_3}')


class C(Gizmo):

    in_3 = param.Number(default=0, allow_refs=True)
    multiplied_by_two = param.Number(default=0)

    def execute(self):
        print(f'C.in_3={self.in_3}')
        print('Multiplying by 2...')
        time.sleep(3)
        self.multiplied_by_two = self.in_3 * 2
        print(f'C.multiplied_by_two={self.multiplied_by_two}')
        print('-'*20)


class CustomCard(pn.Card):

    def __init__(self, parent_template, *args, **kwargs):
        super().__init__(*args, **kwargs)

        spinner = self.objects[0].busy_indicator
        
        # print(pn.widgets.StaticText(value=self.objects[0].name))
        header = pn.Row(
            pn.widgets.StaticText(value=self.objects[0].name),
            spinner
        )

        self.header = header

        self.loading  = parent_template.busy_indicator


if __name__ == '__main__':
    a = A()
    b = B()
    c = C()

    # Make some connections 
    #
    b.in_1 = a.param.out_1
    b.in_2 = a.param.out_2
    c.in_3 = b.param.out_3
    
    # Trigger the run so that we can confirm the pure python implementation works 
    #
    # a.param.trigger('run')

    t = pn.template.BootstrapTemplate()

    ca = CustomCard(t, a)
    cb = CustomCard(t, b)
    cc = CustomCard(t, c)


    display_column = pn.Column()
    display_column.append(ca)
    display_column.append(cb)
    display_column.append(cc)


    display_column.disabled = t.busy_indicator
    t.main.append(display_column)

    pn.serve(t)