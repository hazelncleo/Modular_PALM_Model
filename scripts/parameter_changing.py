from shutil import copyfileobj

if False:
    pars = {'par_1' : 5,
            'par_2' : 10}

    with open('Job-1.inp','r') as f_orig, open('new.inp','w') as f_new:

        # Delete first 4 lines
        f_orig.readline()
        f_orig.readline()
        f_orig.readline()
        f_orig.readline()


        # Write new parameter lines
        f_new.write('*Parameter\n')
        f_new.write('# -------------------------------------\n')
        f_new.write('# --------USER DEFINED PARAMETERS------\n')
        f_new.write('# -------------------------------------\n')

        for item in pars.items():
            f_orig.readline()
            f_new.write(item[0] + ' = ' + str(item[1]) + '\n')

        copyfileobj(f_orig,f_new)

if True:
    mpcci_time = 45e-3

    # THIS IS THE EXACT LINE THAT NEEDS TO BE CHANGED
    line = '\t\t\t\t<param name="TotalTime" modified="true" type="float" value="{}" />\n'.format(mpcci_time)

    # LINE NUMBER -1
    line_n = 316

    
    with open('test.csp', 'r') as f_orig, open('new.csp','w') as f_new:

        for _ in range(line_n):
            f_new.write(f_orig.readline())

        f_orig.readline()
        f_new.write(line)

        copyfileobj(f_orig,f_new)