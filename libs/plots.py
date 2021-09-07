import seaborn as sns
import matplotlib.pyplot as plt


def plot_groups(df):
    sns.set(rc={'figure.figsize':(7,5)})
    sns.set_style('whitegrid')

    ax = sns.barplot(data=df, x='Relative_counts', y='Descuento', 
        hue='Tipo_Producto', hue_order=['Seco', 'Fresco', 'Ultra Fresco'])

    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('discount_and_product.png')
    plt.close()


def plot_subgroups(df):
    sns.set(rc={'figure.figsize':(7,5)})
    sns.set_style('whitegrid')

    for i, j in df.groupby('Descuento'):
        ax = sns.barplot(data=j, x='Relative_counts', y='Descuento', 
            hue='Tipo_Producto', hue_order=['Seco', 'Fresco', 'Ultra Fresco'])

        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig('discount_and_product_{}.png'.format(i))
        plt.close()


def plot_evolution_discount(df, output):

    sns.set(rc={'figure.figsize':(7,5)})
    sns.set_style('whitegrid')

    for i, j in df.groupby('Descuento'):
        ax = sns.barplot(data=j, x='Ejercicio', y='Relative_counts', 
            hue='Tipo_Producto', hue_order=['Seco', 'Fresco', 'Ultra Fresco'])

        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig('evolution_discount_{}.png'.format(i))
        plt.close()
        

def plot_products_discounted(df, output):

    sns.set(rc={'figure.figsize':(7,5)})
    sns.set_style('whitegrid')

    for i, j in df.groupby('Tipo_Producto'):
        j = j.sort_values(by=0, ascending=False)

        palette = sns.color_palette("Blues",n_colors=j.shape[0])
        palette.reverse()
        ax = sns.barplot(data=j, x=0, y='sub_descrip', palette=palette, orient='h')

        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig('Discounted_products_{}.png'.format(i))
        plt.close()