# shadcn/ui: Layout, Navigation & Feedback Components

## Card
```tsx
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card Description</CardDescription>
  </CardHeader>
  <CardContent><p>Card Content</p></CardContent>
  <CardFooter><Button>Action</Button></CardFooter>
</Card>
```

## Tabs
```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

<Tabs defaultValue="account">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">Account settings</TabsContent>
  <TabsContent value="password">Password settings</TabsContent>
</Tabs>
```

## Accordion
```tsx
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>Yes. It adheres to WAI-ARIA design pattern.</AccordionContent>
  </AccordionItem>
</Accordion>
```

## Dialog
```tsx
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild><Button>Open</Button></DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you sure?</DialogTitle>
      <DialogDescription>This action cannot be undone.</DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

## Drawer
```tsx
import { Drawer, DrawerClose, DrawerContent, DrawerDescription, DrawerFooter, DrawerHeader, DrawerTitle, DrawerTrigger } from "@/components/ui/drawer"

<Drawer>
  <DrawerTrigger>Open</DrawerTrigger>
  <DrawerContent>
    <DrawerHeader>
      <DrawerTitle>Title</DrawerTitle>
      <DrawerDescription>Description</DrawerDescription>
    </DrawerHeader>
    <DrawerFooter>
      <Button>Submit</Button>
      <DrawerClose>Cancel</DrawerClose>
    </DrawerFooter>
  </DrawerContent>
</Drawer>
```

## Alert Dialog
```tsx
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog"

<AlertDialog>
  <AlertDialogTrigger asChild><Button variant="destructive">Delete</Button></AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Absolutely sure?</AlertDialogTitle>
      <AlertDialogDescription>This permanently deletes your account.</AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
      <AlertDialogAction>Continue</AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

## Toast
```tsx
import { useToast } from "@/hooks/use-toast"
const { toast } = useToast()
toast({ title: "Scheduled: Catch up", description: "Friday at 5:57 PM" })
```

## Command
```tsx
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"

<Command>
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Suggestions">
      <CommandItem>Calendar</CommandItem>
    </CommandGroup>
  </CommandList>
</Command>
```

## Alert
```tsx
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

<Alert><AlertTitle>Heads up!</AlertTitle><AlertDescription>You can add components using CLI.</AlertDescription></Alert>
<Alert variant="destructive"><AlertTitle>Error</AlertTitle><AlertDescription>Session expired.</AlertDescription></Alert>
```

## Progress & Skeleton
```tsx
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"

<Progress value={33} />
<Skeleton className="h-12 w-12 rounded-full" />
<Skeleton className="h-4 w-[250px]" />
```

## Table
```tsx
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

<Table>
  <TableCaption>Recent invoices</TableCaption>
  <TableHeader><TableRow><TableHead>Invoice</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
  <TableBody><TableRow><TableCell>INV001</TableCell><TableCell>Paid</TableCell></TableRow></TableBody>
</Table>
```

## Avatar & Badge
```tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

<Avatar><AvatarImage src="https://github.com/shadcn.png" /><AvatarFallback>CN</AvatarFallback></Avatar>
<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
```

## Popover & Navigation Menu
```tsx
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
<Popover><PopoverTrigger>Open</PopoverTrigger><PopoverContent>Content</PopoverContent></Popover>

import { NavigationMenu, NavigationMenuContent, NavigationMenuItem, NavigationMenuList, NavigationMenuTrigger } from "@/components/ui/navigation-menu"
<NavigationMenu><NavigationMenuList><NavigationMenuItem>
  <NavigationMenuTrigger>Getting Started</NavigationMenuTrigger>
  <NavigationMenuContent>...</NavigationMenuContent>
</NavigationMenuItem></NavigationMenuList></NavigationMenu>
```
