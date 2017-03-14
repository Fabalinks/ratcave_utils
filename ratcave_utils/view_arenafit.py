import click
import pyglet
import ratcave as rc
from . import cli
from pyglet.window import key

rot_offset = -100.5

@cli.command()
@click.argument('motive_filename', type=click.Path(exists=True))
@click.argument('projector_filename', type=click.Path(exists=True))
@click.argument('arena_filename', type=click.Path(exists=True))
@click.option('--screen', type=int, help='Screen Number for Window to Appear On', default=1)
def view_arenafit(motive_filename, projector_filename, arena_filename, screen):
    # """Displays mesh in .obj file.  Useful for checking that files are rendering properly."""

    reader = rc.WavefrontReader(arena_filename)
    arena = reader.get_mesh('Arena', mean_center=False)
    arena.rotation = arena.rotation.to_quaternion()
    print('Arena Loaded. Position: {}, Rotation: {}'.format(arena.position, arena.rotation))

    camera = rc.Camera.from_pickle(projector_filename)
    camera.projection.fov_y = 39
    light = rc.Light(position=(camera.position.xyz))

    root = rc.EmptyEntity()
    root.add_child(arena)

    sphere = rc.WavefrontReader(rc.resources.obj_primitives).get_mesh('Sphere', scale=.05)
    root.add_child(sphere)

    scene = rc.Scene(meshes=root,
                     camera=camera,
                     light=light,
                     bgColor=(.2, .4, .2))
    scene.gl_states = scene.gl_states[:-1]

    display = pyglet.window.get_platform().get_default_display()
    screen = display.get_screens()[screen]
    window = pyglet.window.Window(fullscreen=True, screen=screen)



    label = pyglet.text.Label()

    shader = rc.Shader.from_file(*rc.resources.genShader)

    @window.event
    def on_draw():
        with shader:
            scene.draw()
        label.draw()

    @window.event
    def on_resize(width, height):
        camera.projection.aspect = float(width) / height



    @window.event
    def on_key_release(sym, mod):
        global rot_offset

        step_size = 1.
        if sym == key.LEFT:
            rot_offset -= step_size
        elif sym == key.RIGHT:
            rot_offset += step_size

        if sym == key.UP:
            scene.camera.projection.fov_y += .5
        elif sym == key.DOWN:
            scene.camera.projection.fov_y -= .5



    import motive
    motive.initialize()
    motive.load_project(motive_filename.encode())
    motive.update()
    rb = motive.get_rigid_bodies()['Arena']

    @window.event
    def update_arena_position(dt):
        motive.update()
        arena.position.xyz = rb.location
        arena.rotation.xyzw = rb.rotation_quats
        rot = arena.rotation.to_euler(units='deg')
        rot.y += rot_offset
        arena.rotation = rot.to_quaternion()
        arena.update()


        sphere.position.xyz = rb.location
        label.text = "off={}, aspect={}, fov_y={}, ({:2f}, {:2f}, {:2f}), ({:2f}, {:2f}, {:2f})".format(rot_offset,
                                                                                                        scene.camera.projection.aspect,
                                                                                                        scene.camera.projection.fov_y,
                                                                                                        *(arena.position.xyz + rb.location))
    pyglet.clock.schedule(update_arena_position)

    def spin_arena(dt):
        # rot = arena.rotation.to_euler()
        # rot.y += 1 * dt
        # arena.rotation = rot.to_quaternion()
        arena.update()
        # arena.rotation.y += 10 * dt
    pyglet.clock.schedule(spin_arena)

    pyglet.app.run()


if __name__ == '__main__':
    view_arenafit()